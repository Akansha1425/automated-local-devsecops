"""
DevSecOps Demo Application
Module: Member 2 — Container Security (Docker + Trivy)
Description: A minimal, hardened Python microservice demonstrating secure containerization.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys

PORT = int(os.environ.get("APP_PORT", 8080))
APP_VERSION = "1.0.0"

class SecureHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'none'")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/status"):
            self._set_headers(200)
            payload = {
                "service": "automated-local-devsecops",
                "module": "Member 2 — Container Security",
                "version": APP_VERSION,
                "status": "healthy",
                "non_root": os.getuid() != 0 if hasattr(os, "getuid") else "n/a",
            }
            self.wfile.write(json.dumps(payload, indent=2).encode("utf-8"))
        elif self.path == "/health":
            self._set_headers(200)
            self.wfile.write(b'{"status":"UP"}')
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Not Found"}')

    def log_message(self, format, *args):
        # Structured log output to stdout
        sys.stdout.write(f"[INFO] {self.address_string()} - {format % args}\n")
        sys.stdout.flush()

def run():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, SecureHandler)
    sys.stdout.write(f"[STARTUP] DevSecOps demo app listening on port {PORT}\n")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("[SHUTDOWN] Server stopped\n")
        sys.stdout.flush()
        httpd.server_close()

if __name__ == "__main__":
    run()
