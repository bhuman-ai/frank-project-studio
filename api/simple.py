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
        
        # Get the actual docs from GitHub
        import requests
        
        doc_name = path if path.endswith('.md') else f"{path}.md"
        
        github_urls = {
            'project.md': 'https://raw.githubusercontent.com/bhuman-ai/gesture_generator/main/target-docs/project.md',
            'technical.md': 'https://raw.githubusercontent.com/bhuman-ai/gesture_generator/main/target-docs/technical.md',
            'interface.md': 'https://raw.githubusercontent.com/bhuman-ai/gesture_generator/main/target-docs/interface.md'
        }
        
        content = "# Loading..."
        if doc_name in github_urls:
            try:
                r = requests.get(github_urls[doc_name])
                if r.status_code == 200:
                    content = r.text
            except:
                content = "# Error loading from GitHub"
        
        response = {
            'content': content,
            'lines': len(content.split('\n'))
        }
        
        self.wfile.write(json.dumps(response).encode())
        return