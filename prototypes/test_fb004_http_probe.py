import json
import unittest
from unittest.mock import patch, MagicMock
from fb004_http_probe import ERRORS, payload, probe, verify


class ContractTests(unittest.TestCase):
    def test_negative_contracts(self):
        for case, error in ERRORS.items():
            body = dict(ok=False, request_id=None if case == 'invalid-request-id' else 'fb004_001', errors=[error])
            raw = json.dumps(body).encode()
            verify(case, 400, 'application/json; charset=utf-8', raw)
            for status, content_type, value in [(200,'application/json',raw),
                    (400,'text/html',raw), (400,'application/json',b''),
                    (400,'application/json',b'{"ok":false,"errors":[]}')]:
                with self.assertRaises((ValueError, TypeError)):
                    verify(case,status,content_type,value)

    def test_transport_destination_no_redirect_or_retry(self):
        with patch('fb004_http_probe.http.client.HTTPConnection') as factory:
            conn = factory.return_value
            response = conn.getresponse.return_value
            response.status = 302
            response.read.return_value = b''
            response.getheader.return_value = 'text/html'
            with self.assertRaises(ValueError):
                probe('valid')
            factory.assert_called_once_with('127.0.0.1',5678,timeout=10)
            conn.request.assert_called_once_with('POST','/webhook-test/fb003-demo',
                json.dumps(payload('valid')), {'Content-Type':'application/json'})
            conn.close.assert_called_once()

    def test_response_cap(self):
        with patch('fb004_http_probe.http.client.HTTPConnection') as factory:
            response = factory.return_value.getresponse.return_value
            response.read.return_value = b'x' * 4097
            with self.assertRaises(ValueError):
                probe('valid')
            response.read.assert_called_once_with(4097)


if __name__ == '__main__':
    unittest.main()
