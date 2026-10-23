"""One synthetic request to an explicitly armed local n8n test webhook; no retries."""
import argparse
import http.client
import json

ERRORS = {
    'invalid-intent': 'intent must be support, sales, or other',
    'invalid-email': 'email must be a valid address',
    'invalid-request-id': 'request_id must be 3-64 letters, digits, underscores or hyphens',
}


class ContractError(ValueError):
    """Safe diagnostic composed locally, never from a remote body."""


def payload(case):
    body = dict(request_id='fb004_001', email='demo@example.org', intent='support')
    changes = {'invalid-intent': ('intent', 'unknown'),
               'invalid-email': ('email', 'not-an-email'),
               'invalid-request-id': ('request_id', '<invalid>')}
    if case in changes:
        key, value = changes[case]
        body[key] = value
    return body


def verify(case, status, content_type, raw):
    expected = 200 if case == 'valid' else 400
    if status != expected:
        raise ContractError(f'expected HTTP {expected}, got {status}')
    if content_type.split(';')[0].strip().lower() != 'application/json':
        raise ContractError('expected application/json')
    body = json.loads(raw)
    if case == 'valid':
        wanted = dict(ok=True, request_id='fb004_001', provider='local-mock',
                      result=dict(route='helpdesk', accepted=True))
    else:
        wanted = dict(ok=False, request_id=None if case == 'invalid-request-id' else 'fb004_001',
                      errors=[ERRORS[case]])
    if body != wanted:
        raise ContractError('response contract mismatch (body suppressed)')


def probe(case):
    # Fixed numeric loopback: no DNS, proxies, redirects, arbitrary URLs or production path.
    conn = http.client.HTTPConnection('127.0.0.1', 5678, timeout=10)
    try:
        conn.request('POST', '/webhook-test/fb003-demo', json.dumps(payload(case)),
                     {'Content-Type': 'application/json'})
        response = conn.getresponse()
        raw = response.read(4097)
        if len(raw) > 4096:
            raise ContractError('response exceeds 4096-byte limit')
        verify(case, response.status, response.getheader('Content-Type', ''), raw)
        return {'case': case, 'status': response.status, 'passed': True,
                'verification': 'live HTTP endpoint; operator must confirm imported workflow identity'}
    finally:
        conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', choices=['valid', *ERRORS])
    args = parser.parse_args()
    try:
        print(json.dumps(probe(args.case)))
    except Exception as exc:
        # Never print response bodies, headers, server errors or credentials.
        print(json.dumps({'case': args.case, 'passed': False, 'error_type': type(exc).__name__,
                          'detail': str(exc) if isinstance(exc, ContractError) else 'transport or JSON decoding failed',
                          'next_gate': 'Confirm local listener, re-arm test webhook, inspect sanitized contract locally.'}))
        raise SystemExit(1)
