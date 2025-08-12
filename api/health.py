"""
Vercel Serverless Function - Health Check
"""

import json
import os
import requests

BACKEND_URL = os.environ.get('CODESPACE_URL', '')

def handler(request, response):
    """Health check endpoint"""
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    if request.method == 'OPTIONS':
        response.status_code = 200
        response.headers = headers
        return response
    
    # Check backend health
    backend_status = 'not configured'
    claude_available = False
    
    if BACKEND_URL:
        try:
            backend_response = requests.get(
                f"{BACKEND_URL}/health",
                timeout=5
            )
            if backend_response.ok:
                data = backend_response.json()
                backend_status = 'connected'
                claude_available = data.get('claude', False)
        except:
            backend_status = 'unreachable'
    
    response.status_code = 200
    response.headers = headers
    response.body = json.dumps({
        'status': 'healthy',
        'backend': backend_status,
        'claude': claude_available,
        'backend_url': BACKEND_URL[:30] + '...' if BACKEND_URL else None
    })
    
    return response