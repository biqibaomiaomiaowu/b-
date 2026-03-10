
import http.client
import subprocess
import time
import sys
import unittest

class TestCORSSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the server
        cls.proc = subprocess.Popen([sys.executable, "bilibili_media_webui.py", "--no-open"])
        time.sleep(2) # Wait for server to start

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait()

    def test_allowed_origin_127_0_0_1_8767(self):
        conn = http.client.HTTPConnection("127.0.0.1", 8767)
        origin = "http://127.0.0.1:8767"
        conn.request("OPTIONS", "/api/tool-detect", headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST"
        })
        res = conn.getresponse()
        self.assertEqual(res.status, 204)
        headers = dict(res.getheaders())
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), origin)
        self.assertEqual(headers.get("Vary"), "Origin")

    def test_allowed_origin_localhost_5173(self):
        conn = http.client.HTTPConnection("127.0.0.1", 8767)
        origin = "http://localhost:5173"
        conn.request("OPTIONS", "/api/tool-detect", headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST"
        })
        res = conn.getresponse()
        self.assertEqual(res.status, 204)
        headers = dict(res.getheaders())
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), origin)
        self.assertEqual(headers.get("Vary"), "Origin")

    def test_allowed_origin_ipv6_loopback(self):
        conn = http.client.HTTPConnection("127.0.0.1", 8767)
        origin = "http://[::1]:8767"
        conn.request("OPTIONS", "/api/tool-detect", headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST"
        })
        res = conn.getresponse()
        self.assertEqual(res.status, 204)
        headers = dict(res.getheaders())
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), origin)
        self.assertEqual(headers.get("Vary"), "Origin")

    def test_disallowed_origin_malicious(self):
        conn = http.client.HTTPConnection("127.0.0.1", 8767)
        origin = "http://malicious.com"
        conn.request("OPTIONS", "/api/tool-detect", headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST"
        })
        res = conn.getresponse()
        self.assertEqual(res.status, 204)
        headers = dict(res.getheaders())
        self.assertIsNone(headers.get("Access-Control-Allow-Origin"))

if __name__ == "__main__":
    unittest.main()
