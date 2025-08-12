from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        BACKEND_URL = os.environ.get('CODESPACE_URL', '')
        
        # Check backend health
        backend_status = 'not configured'
        claude_available = False
        
        if BACKEND_URL:
            try:
                backend_response = requests.get(
                    f"{BACKEND_URL}/health",
                    timeout=None  # NO TIMEOUT!
                )
                if backend_response.ok:
                    data = backend_response.json()
                    backend_status = 'connected'
                    claude_available = data.get('claude', False)
            except:
                backend_status = 'unreachable'
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'status': 'healthy',
            'backend': backend_status,
            'claude': claude_available,
            'backend_url': BACKEND_URL[:30] + '...' if BACKEND_URL else None
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return