from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse

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
                # Ensure URL doesn't have trailing slash
                backend_url = BACKEND_URL.rstrip('/')
                
                # Prepare request
                url = f"{backend_url}/api/message"
                data = json.dumps({'message': message, 'context': context}).encode('utf-8')
                
                req = urllib.request.Request(url, data=data)
                req.add_header('Content-Type', 'application/json')
                req.add_header('Accept', 'application/json')
                
                # Make request (no timeout)
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode('utf-8'))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                import traceback
                error_details = str(e)
                
                # Check if it's a connection error
                if "urlopen error" in str(e) or "HTTP Error" in str(e):
                    help_msg = "Make sure your Codespace port 8080 is set to PUBLIC visibility. In your Codespace, go to Ports tab and change 8080 visibility from Private to Public."
                else:
                    help_msg = "Check backend logs in your Codespace terminal."
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'response': f"Cannot reach backend at {BACKEND_URL}. {help_msg}",
                    'error': error_details,
                    'help': help_msg
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