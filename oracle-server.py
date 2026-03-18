#!/usr/bin/env python3
"""Local dev server for oracle.html — serves static files and proxies /proxy to Anthropic API."""
import http.server, json, urllib.request, urllib.error, os, sys

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence request logs

    def send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_POST(self):
        if self.path != '/proxy':
            self.send_response(404); self.end_headers(); return

        length   = int(self.headers.get('Content-Length', 0))
        body     = self.rfile.read(length)
        api_key  = self.headers.get('x-api-key', '')

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=body,
            headers={
                'Content-Type':      'application/json',
                'x-api-key':         api_key,
                'anthropic-version': '2023-06-01',
            }
        )
        try:
            with urllib.request.urlopen(req) as r:
                resp = r.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_cors()
                self.end_headers()
                self.wfile.write(resp)
        except urllib.error.HTTPError as e:
            resp = e.read()
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_cors()
            self.end_headers()
            self.wfile.write(resp)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
port = 8765
print(f'Oracle server → http://localhost:{port}/oracle.html')
http.server.HTTPServer(('localhost', port), Handler).serve_forever()
