from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        BACKEND_URL = os.environ.get('CODESPACE_URL', '')
        
        # Extract doc name from path - handle /api/docs/project format
        if '/api/docs/' in self.path:
            doc_name = self.path.split('/api/docs/')[-1]
        else:
            path_parts = self.path.split('/')
            doc_name = path_parts[-1] if path_parts else 'project'
        
        # Ensure .md extension
        if not doc_name.endswith('.md'):
            doc_name = doc_name + '.md'
        
        # If backend configured, fetch document
        if BACKEND_URL:
            try:
                backend_response = requests.get(
                    f"{BACKEND_URL}/api/docs/{doc_name}",
                    timeout=30  # Reasonable timeout for docs
                )
                
                result = backend_response.json()
                
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
                    'content': f"# {doc_name}\n\nError loading from backend: {str(e)}",
                    'lines': 2,
                    'error': str(e)
                }).encode())
        else:
            # Fetch from GitHub directly
            github_urls = {
                'project.md': 'https://raw.githubusercontent.com/bhuman-ai/gesture_generator/main/target-docs/project.md',
                'technical.md': 'https://raw.githubusercontent.com/bhuman-ai/gesture_generator/main/target-docs/technical.md',
                'interface.md': 'https://raw.githubusercontent.com/bhuman-ai/gesture_generator/main/target-docs/interface.md'
            }
            
            content = None
            if doc_name in github_urls:
                try:
                    github_response = requests.get(github_urls[doc_name], timeout=5)
                    if github_response.status_code == 200:
                        content = github_response.text
                except Exception as e:
                    content = f"# {doc_name}\n\nError loading from GitHub: {str(e)}"
            
            if not content:
                # Fallback demo content
                demo_content = {
                    'project.md': "# Project Blueprint\n\n*Loading from GitHub...*",
                    'technical.md': "# Technical Blueprint\n\n*Loading from GitHub...*",
                    'interface.md': "# Interface Blueprint\n\n*Loading from GitHub...*"
                }
                content = demo_content.get(doc_name, f"# {doc_name}\n\nDocument not found.")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'content': content,
                'lines': len(content.split('\n')),
                'demo': True
            }).encode())
        
        return
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return