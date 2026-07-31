import os
import sys
import subprocess

# Add project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("Streamlit server initialized. Accessing via serverless handler. Note: Serverless functions are stateless and do not support persistent WebSockets.".encode('utf-8'))
        return