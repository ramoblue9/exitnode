from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import socket
import json
from datetime import datetime

import os
PORT = int(os.environ.get("PORT", 6008))

class ExitNodeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path in ("/", "/status"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data = {
                "status": "online",
                "port": PORT,
                "time": datetime.utcnow().isoformat() + "Z",
                "host": socket.gethostname()
            }
            self.wfile.write(json.dumps(data).encode())
            return

        if self.path.startswith("/proxy?"):
            target = self.path[7:]
            if not target.startswith("http"):
                target = "http://" + target
            try:
                req = Request(target, headers={"User-Agent": "ExitNode/1.0"})
                with urlopen(req, timeout=15) as resp:
                    body = resp.read()
                    self.send_response(resp.getcode())
                    self.send_header("Content-Type", resp.headers.get("Content-Type", "text/plain"))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(body)
            except Exception as e:
                self.send_response(502)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(str(e).encode())
            return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

def main():
    server = HTTPServer(("0.0.0.0", PORT), ExitNodeHandler)
    print(f"Exit node running on port {PORT}")
    server.serve_forever()

if __name__ == "__main__":
    main()
