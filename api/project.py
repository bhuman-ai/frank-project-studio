from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import ssl

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        BACKEND_URL = os.environ.get('CODESPACE_URL', '')
        
        # Parse request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            body = json.loads(post_data)
            github_url = body.get('github_url', '')
        except:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid request'}).encode())
            return
        
        # Forward to backend
        if BACKEND_URL:
            try:
                # Prepare request
                backend_url = BACKEND_URL.rstrip('/')
                url = f"{backend_url}/api/project"
                data = json.dumps({'github_url': github_url}).encode('utf-8')
                
                req = urllib.request.Request(url, data=data)
                req.add_header('Content-Type', 'application/json')
                req.add_header('Accept', 'application/json')
                
                # Disable SSL verification for Codespace URLs (they use self-signed certs)
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                # Make request
                with urllib.request.urlopen(req, context=ctx) as response:
                    result = json.loads(response.read().decode('utf-8'))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': str(e)
                }).encode())
        else:
            # Demo response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'name': github_url.split('/')[-1],
                'file_count': 0,
                'status': 'Demo mode - connect backend',
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