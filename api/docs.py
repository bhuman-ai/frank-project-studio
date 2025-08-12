from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        BACKEND_URL = os.environ.get('CODESPACE_URL', '')
        
        # Extract doc name from path
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
                    timeout=10
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
            # Demo content
            demo_content = {
                'project.md': """# Project Blueprint

## Vision
*Connect your GitHub Codespace to start building your project blueprint.*

## Features
- Real-time document updates
- Natural conversation with Frank
- Mobile-friendly interface

## Setup
1. Run backend in GitHub Codespace
2. Set CODESPACE_URL in Vercel
3. Start chatting with Frank!""",
                
                'technical.md': """# Technical Blueprint

## Architecture
- Frontend: Vercel (this app)
- Backend: GitHub Codespace
- AI: Claude CLI

## Stack
- HTML/CSS/JavaScript
- Python Flask backend
- Vercel serverless functions""",
                
                'interface.md': """# Interface Blueprint

## Design
- Mobile-first responsive design
- Real-time chat interface
- Live document viewer

## Features
- Swipe between chat and docs
- Auto-updating blueprints
- Persistent sessions"""
            }
            
            content = demo_content.get(doc_name, f"# {doc_name}\n\nDocument will be created as you chat.")
            
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