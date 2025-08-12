from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Extract doc name from path
        path = self.path.split('/')[-1] if '/' in self.path else 'project.md'
        
        # Hardcoded test response
        test_content = """# Project.md

## This is a test

The real docs will load from GitHub once we fix the API.

For now, this proves the API endpoint is working."""
        
        response = {
            'content': test_content,
            'lines': 7,
            'test': True
        }
        
        self.wfile.write(json.dumps(response).encode())
        return