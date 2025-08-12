from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        BACKEND_URL = os.environ.get('CODESPACE_URL', '')
        
        # Parse request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            body = json.loads(post_data)
            message = body.get('message', '')
            context = body.get('context', '')
        except:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid request'}).encode())
            return
        
        # If backend is configured, forward request
        if BACKEND_URL:
            try:
                backend_response = requests.post(
                    f"{BACKEND_URL}/api/message",
                    json={'message': message, 'context': context},
                    timeout=None  # NO TIMEOUT - Let Claude think as long as needed!
                )
                
                result = backend_response.json()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except requests.Timeout:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'response': "Frank's taking a moment to think... Try again.",
                    'error': 'timeout'
                }).encode())
                
            except Exception as e:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'response': f"Connection issue. Make sure Codespace is running.",
                    'error': str(e)
                }).encode())
        else:
            # Demo mode - no backend
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'response': f"Frank here. I got: '{message}'. Set CODESPACE_URL in Vercel.",
                'demo': True
            }).encode())
        
        return
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return