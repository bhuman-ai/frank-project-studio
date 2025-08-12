from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Handle CORS preflight
        if self.command == 'OPTIONS':
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            return
            
        # Extract doc name from query params or path
        import urllib.parse
        parsed = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed.query)
        
        # Get doc name from query param or default to project
        doc_name = query_params.get('doc', ['project'])[0]
        
        # GitHub URLs for the actual docs
        github_urls = {
            'project': 'https://raw.githubusercontent.com/bhuman-ai/gesture_generator/main/target-docs/project.md',
            'technical': 'https://raw.githubusercontent.com/bhuman-ai/gesture_generator/main/target-docs/technical.md',
            'interface': 'https://raw.githubusercontent.com/bhuman-ai/gesture_generator/main/target-docs/interface.md'
        }
        
        content = "# Document Not Found\n\nRequested document not available."
        
        if doc_name in github_urls:
            try:
                # Use urllib with GitHub token for private repo access
                import os
                token = os.environ.get('GITHUB_TOKEN', '')
                
                req = urllib.request.Request(github_urls[doc_name])
                if token:
                    req.add_header('Authorization', f'token {token}')
                
                with urllib.request.urlopen(req) as response:
                    content = response.read().decode('utf-8')
            except Exception as e:
                content = f"# Error Loading Document\n\nFailed to fetch from GitHub: {str(e)}"
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_data = {
            'content': content,
            'lines': len(content.split('\n')),
            'doc': doc_name
        }
        
        self.wfile.write(json.dumps(response_data).encode())
        return