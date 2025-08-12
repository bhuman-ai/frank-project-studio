"""
Vercel Serverless Function - Docs Endpoint
Fetches blueprint documents from backend
"""

import json
import os
import requests

BACKEND_URL = os.environ.get('CODESPACE_URL', '')

def handler(request, response):
    """Vercel serverless function handler"""
    
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # Handle preflight
    if request.method == 'OPTIONS':
        response.status_code = 200
        response.headers = headers
        return response
    
    # Extract doc name from path
    path_parts = request.path.split('/')
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
            response.status_code = 200
            response.headers = headers
            response.body = json.dumps(result)
            
        except Exception as e:
            response.status_code = 200
            response.headers = headers
            response.body = json.dumps({
                'content': f"# {doc_name}\n\nError loading from backend: {str(e)}",
                'lines': 2,
                'error': str(e)
            })
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
        
        response.status_code = 200
        response.headers = headers
        response.body = json.dumps({
            'content': content,
            'lines': len(content.split('\n')),
            'demo': True
        })
    
    return response