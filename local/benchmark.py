"""Bounded Windows localhost benchmark; standard library only. Never downloads models."""
import argparse
import ctypes
import hashlib
import json
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = 'http://127.0.0.1:11434'
CANDIDATES = ['qwen2.5-coder:3B', 'llama3.2:3B', 'phi3:latest']
GIB = 1024 ** 3

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, 'Redirect refused', headers, fp)

def local_opener():
    # Ignore environment proxy settings and refuse even localhost redirects.
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

class Memory(ctypes.Structure):
    _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [(x, ctypes.c_ulonglong) for x in ['total', 'free', 'page_total', 'page_free', 'virtual_total', 'virtual_free', 'extended']]

def memory():
    m = Memory(); m.length = ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise OSError('Cannot verify memory; refusing inference')
    return {'total_bytes': m.total, 'free_bytes': m.free, 'load_percent': m.load}

def cpu_ticks():
    vals = [ctypes.c_ulonglong() for _ in range(3)]
    if not ctypes.windll.kernel32.GetSystemTimes(*[ctypes.byref(v) for v in vals]):
        raise OSError('Cannot read CPU counters')
    return tuple(v.value for v in vals)

def call(route, payload=None):
    if route not in ('/api/ps', '/api/tags', '/api/generate'):
        raise ValueError('Unsupported localhost route')
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE + route, data=data, headers={'Content-Type': 'application/json'})
    with local_opener().open(req, timeout=90 if payload else 5) as r:
        return json.load(r)

def eligible(model, free):
    return (model.get('name') in CANDIDATES and ':cloud' not in model['name']
            and not model.get('remote_host') and not model.get('remote_model')
            and model.get('details', {}).get('format') == 'gguf'
            and 0 < model.get('size', 0) <= 3 * GIB
            and free >= model['size'] + 2 * GIB)

def payload(name):
    return {'model': name, 'stream': False, 'format': 'json', 'keep_alive': 0,
            'options': {'num_ctx': 1024, 'num_predict': 128, 'temperature': 0, 'seed': 7, 'num_thread': 2},
            'prompt': 'Return only a JSON object with exactly three keys. The source text is: Order FB-17 has 3 units at 12 dollars each. Set order_id to the order identifier, units to the integer unit count, and total to the integer total price. Do not add facts.'}

def grade(text):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError('Non-standard JSON constant')
    try:
        obj = json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid_constant)
        schema = (isinstance(obj, dict) and set(obj) == {'order_id', 'units', 'total'}
                  and type(obj['units']) is int and type(obj['total']) is int
                  and isinstance(obj['order_id'], str))
        return {'json_valid': True, 'schema_valid': schema,
                'exact_accuracy': schema and obj == {'order_id': 'FB-17', 'units': 3, 'total': 36}}
    except (ValueError, TypeError):
        return {'json_valid': False, 'schema_valid': False, 'exact_accuracy': False}

def run():
    report = {'observed_at': datetime.now(timezone.utc).isoformat(), 'paid_calls': 0,
              'scope': 'synthetic extraction only; not general intelligence or endurance', 'trials': []}
    try:
        return _run(report)
    except Exception as e:
        # Preflight/timeouts must leave a usable result; do not persist exception text.
        report.update(status='stopped_preflight_or_resource_error', error_type=type(e).__name__)
        return report

def _run(report):
    report['memory_before'] = memory()
    if call('/api/ps').get('models'):
        report['status'] = 'blocked_existing_loaded_model'; return report
    models = {m['name']: m for m in call('/api/tags')['models']}
    selected = [models[n] for n in CANDIDATES if n in models and eligible(models[n], memory()['free_bytes'])]
    report['selected_models'] = [{'name': m['name'], 'digest': m.get('digest'), 'size': m['size']} for m in selected]
    if not selected:
        report['status'] = 'blocked_insufficient_memory_or_no_eligible_model'; return report
    # Invalid model returns an error without downloading. Recovery is the next successful trial.
    try:
        call('/api/generate', payload('fb-deliberately-missing-test-model:absent'))
        report['invalid_model_test'] = 'unexpected_success'; report['status'] = 'stopped'; return report
    except urllib.error.HTTPError as e:
        report['invalid_model_http_status'] = e.code
        if e.code != 404:
            report['status'] = 'stopped_unexpected_failure'; return report
    for model in selected:
        for trial in range(2):
            if call('/api/ps').get('models') or not eligible(model, memory()['free_bytes']):
                report['status'] = 'stopped_resource_gate'; return report
            samples = []; stop = threading.Event()
            def sample():
                previous = cpu_ticks()
                while not stop.wait(0.5):
                    current = cpu_ticks(); delta = [b-a for a,b in zip(previous,current)]
                    total = delta[1] + delta[2]
                    samples.append({**memory(), 'system_cpu_percent': 100*(1-delta[0]/total) if total else None})
                    previous = current
            thread = threading.Thread(target=sample, daemon=True); thread.start()
            started = time.monotonic()
            request = payload(model['name'])
            row = {'model': model['name'], 'model_digest': model.get('digest'), 'trial': trial+1,
                   'request': request, 'request_sha256': hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()}
            try:
                result = call('/api/generate', request)
                row['response'] = result.get('response', '')
                row['response_sha256'] = hashlib.sha256(row['response'].encode()).hexdigest()
                row.update(grade(result.get('response', '')))
                row.update({'done': result.get('done'), 'done_reason': result.get('done_reason'),
                            'eval_count': result.get('eval_count'), 'load_duration_ns': result.get('load_duration')})
            except Exception as e:
                row['error_type'] = type(e).__name__
            finally:
                stop.set(); thread.join(2)
            row['wall_seconds'] = round(time.monotonic()-started, 3)
            row['samples'] = samples; report['trials'].append(row)
            if 'error_type' in row:
                report['status'] = 'stopped_inference_error_no_retry'; return report
            time.sleep(1)
    report['status'] = 'completed_bounded_benchmark'
    report['recovery_verified'] = any(r.get('exact_accuracy') for r in report['trials'])
    return report

def write_report(path, report):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(report, indent=2), encoding='utf-8')
    temporary.replace(path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = run()
    write_report(args.output, result)
    print(json.dumps({'status': result['status'], 'trials': len(result['trials'])}))
