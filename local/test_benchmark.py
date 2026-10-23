import unittest
import json
import hashlib
from pathlib import Path
import tempfile
from unittest.mock import patch
import urllib.error
import benchmark as b

class Gates(unittest.TestCase):
    def setUp(self):
        self.model = {'name': 'qwen2.5-coder:3B', 'size': 2*b.GIB, 'details': {'format': 'gguf'}}
    def test_low_memory(self):
        self.assertFalse(b.eligible(self.model, b.GIB))
    def test_sufficient_memory(self):
        self.assertTrue(b.eligible(self.model, 5*b.GIB))
    def test_cloud(self):
        self.model['remote_model'] = 'cloud-model'
        self.assertFalse(b.eligible(self.model, 20*b.GIB))
    def test_unknown_model(self):
        self.model['name'] = 'other'
        self.assertFalse(b.eligible(self.model, 20*b.GIB))
    def test_accuracy(self):
        self.assertTrue(b.grade('{"order_id":"FB-17","units":3,"total":36}')['exact_accuracy'])
    def test_bad_math(self):
        self.assertFalse(b.grade('{"order_id":"FB-17","units":3,"total":35}')['exact_accuracy'])
    def test_extra_key(self):
        self.assertFalse(b.grade('{"order_id":"FB-17","units":3,"total":36,"extra":0}')['schema_valid'])
    def test_bad_json(self):
        self.assertFalse(b.grade('bad')['json_valid'])
    def test_duplicate_keys_and_nonstandard_constants(self):
        self.assertFalse(b.grade('{"order_id":"FB-17","units":99,"units":3,"total":36}')['json_valid'])
        self.assertFalse(b.grade('{"order_id":"FB-17","units":3,"total":NaN}')['json_valid'])
    def test_redirect_and_proxy_gate(self):
        request = b.urllib.request.Request(b.BASE + '/api/tags')
        with self.assertRaises(urllib.error.HTTPError):
            b.NoRedirect().redirect_request(request, None, 302, 'redirect', {}, 'https://example.com')
        with patch.object(b.urllib.request, 'ProxyHandler', wraps=b.urllib.request.ProxyHandler) as proxy, patch.object(b.urllib.request, 'build_opener'):
            b.local_opener()
            proxy.assert_called_once_with({})
        with self.assertRaises(ValueError): b.call('/unexpected')
    def test_preflight_timeout_is_persistable(self):
        with patch.object(b, 'memory', return_value={'free_bytes': 8*b.GIB}), patch.object(b, 'call', side_effect=TimeoutError()):
            result = b.run()
        self.assertEqual('stopped_preflight_or_resource_error', result['status'])
        self.assertEqual('TimeoutError', result['error_type'])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'nested' / 'result.json'
            b.write_report(path, result)
            self.assertEqual(result, json.loads(path.read_text()))
            self.assertFalse(path.with_name('result.json.tmp').exists())
    def test_trial_receipt_is_reproducible(self):
        model = dict(self.model, digest='synthetic-digest')
        answer = '{"order_id":"FB-17","units":3,"total":36}'
        responses = [{'models': []}, {'models': [model]}, urllib.error.HTTPError('local', 404, 'synthetic', None, None),
                     {'models': []}, {'response': answer, 'done': True}, {'models': []}, {'response': answer, 'done': True}]
        with patch.object(b, 'memory', return_value={'free_bytes': 8*b.GIB}), patch.object(b, 'cpu_ticks', return_value=(0, 0, 0)), patch.object(b, 'call', side_effect=responses), patch.object(b.time, 'sleep'):
            result = b.run()
        self.assertEqual('completed_bounded_benchmark', result['status'])
        self.assertEqual(2, len(result['trials']))
        row = result['trials'][0]
        self.assertEqual('synthetic-digest', row['model_digest'])
        self.assertEqual(b.payload(model['name']), row['request'])
        self.assertEqual(answer, row['response'])
        self.assertEqual(hashlib.sha256(answer.encode()).hexdigest(), row['response_sha256'])
    def test_n8n_template_is_inactive_read_only_and_connected(self):
        workflow = json.loads((Path(__file__).parent / 'n8n-ollama-health.json').read_text())
        self.assertFalse(workflow['active'])
        self.assertEqual(2, len(workflow['nodes']))
        trigger, request = workflow['nodes']
        self.assertEqual('n8n-nodes-base.manualTrigger', trigger['type'])
        self.assertEqual('GET', request['parameters']['method'])
        self.assertEqual('http://host.docker.internal:11434/api/version', request['parameters']['url'])
        self.assertEqual(5000, request['parameters']['options']['timeout'])
        self.assertEqual(request['name'], workflow['connections'][trigger['name']]['main'][0][0]['node'])
        self.assertFalse(any('credentials' in node for node in workflow['nodes']))
    def test_bounds(self):
        p = b.payload('qwen2.5-coder:3B')
        self.assertEqual(p['keep_alive'], 0)
        self.assertLessEqual(p['options']['num_ctx'], 1024)
        self.assertLessEqual(p['options']['num_predict'], 128)
    def test_occupied_model_stops_without_generate(self):
        with patch.object(b, 'memory', return_value={'free_bytes': 8*b.GIB}), patch.object(b, 'call', return_value={'models': [{'name': 'other'}]}) as call:
            self.assertEqual(b.run()['status'], 'blocked_existing_loaded_model')
            call.assert_called_once_with('/api/ps')
    def test_invalid_model_unexpected_error_stops(self):
        responses = [{'models': []}, {'models': [self.model]}, urllib.error.HTTPError('local', 500, 'synthetic', None, None)]
        with patch.object(b, 'memory', return_value={'free_bytes': 8*b.GIB}), patch.object(b, 'call', side_effect=responses) as call:
            self.assertEqual(b.run()['status'], 'stopped_unexpected_failure')
            self.assertEqual(call.call_count, 3)
    def test_timeout_stops_without_retry(self):
        responses = [{'models': []}, {'models': [self.model]}, urllib.error.HTTPError('local', 404, 'synthetic', None, None), {'models': []}, TimeoutError()]
        with patch.object(b, 'memory', return_value={'free_bytes': 8*b.GIB}), patch.object(b, 'cpu_ticks', return_value=(0, 0, 0)), patch.object(b, 'call', side_effect=responses) as call:
            result = b.run()
            self.assertEqual(result['status'], 'stopped_inference_error_no_retry')
            self.assertEqual(len(result['trials']), 1)
            self.assertEqual(call.call_count, 5)

if __name__ == '__main__':
    unittest.main()
