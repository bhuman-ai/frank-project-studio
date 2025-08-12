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
        
        # GitHub API URLs for the actual docs
        github_api_urls = {
            'project': 'https://api.github.com/repos/bhuman-ai/gesture_generator/contents/target-docs/project.md',
            'technical': 'https://api.github.com/repos/bhuman-ai/gesture_generator/contents/target-docs/technical.md',
            'interface': 'https://api.github.com/repos/bhuman-ai/gesture_generator/contents/target-docs/interface.md'
        }
        
        content = "# Document Not Found\n\nRequested document not available."
        
        if doc_name in github_api_urls:
            try:
                import os
                token = os.environ.get('GITHUB_TOKEN', '')
                
                req = urllib.request.Request(github_api_urls[doc_name])
                req.add_header('Accept', 'application/vnd.github.v3.raw')
                if token:
                    req.add_header('Authorization', f'token {token}')
                
                with urllib.request.urlopen(req) as response:
                    content = response.read().decode('utf-8')
            except Exception as e:
                content = f"# Error Loading Document\n\nFailed to fetch from GitHub API: {str(e)}\n\nMake sure GITHUB_TOKEN is set in Vercel environment variables."
        
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