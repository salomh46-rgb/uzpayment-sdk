import http.server
import socketserver
import json
import urllib.parse
from ..security.signature import SignatureValidator

def run_mock_payment_server(port=8080, service_id="12345", secret_key="test_secret"):
    class MockHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            print(f"\n[MOCK SERVER] Incoming {self.path}:")
            print(f"Headers: {dict(self.headers)}")
            print(f"Body: {body}")
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "MOCK_OK", "received": true}')

    print(f"🚀 UzPayment Mock Server running on http://localhost:{port}")
    with socketserver.TCPServer(("", port), MockHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped mock server.")
