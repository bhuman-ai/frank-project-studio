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
                backend_response = requests.post(
                    f"{BACKEND_URL}/api/project",
                    json={'github_url': github_url},
                    timeout=60  # Increased timeout for large repos
                )
                
                # Check if response is JSON
                try:
                    result = backend_response.json()
                except json.JSONDecodeError:
                    # Backend returned non-JSON (probably HTML error page)
                    result = {
                        'success': False,
                        'error': f'Backend error: {backend_response.status_code}',
                        'details': backend_response.text[:200]
                    }
                
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