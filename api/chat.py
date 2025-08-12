"""
Vercel Serverless Function - Chat Endpoint
Connects to GitHub Codespace backend
"""

import json
import os
import requests
from urllib.parse import parse_qs

# Get backend URL from environment
BACKEND_URL = os.environ.get('CODESPACE_URL', '')

def handler(request, response):
    """Vercel serverless function handler"""
    
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # Handle preflight
    if request.method == 'OPTIONS':
        response.status_code = 200
        response.headers = headers
        return response
    
    # Parse request body
    try:
        body = json.loads(request.body)
        message = body.get('message', '')
        context = body.get('context', '')
    except:
        response.status_code = 400
        response.headers = headers
        response.body = json.dumps({'error': 'Invalid request'})
        return response
    
    # If backend is configured, forward request
    if BACKEND_URL:
        try:
            backend_response = requests.post(
                f"{BACKEND_URL}/api/message",
                json={'message': message, 'context': context},
                timeout=30
            )
            
            result = backend_response.json()
            response.status_code = 200
            response.headers = headers
            response.body = json.dumps(result)
            
        except requests.Timeout:
            response.status_code = 200
            response.headers = headers
            response.body = json.dumps({
                'response': "Frank's taking a moment to think... Try again.",
                'error': 'timeout'
            })
            
        except Exception as e:
            response.status_code = 200
            response.headers = headers
            response.body = json.dumps({
                'response': f"Connection issue. Make sure Codespace is running on {BACKEND_URL}",
                'error': str(e)
            })
    else:
        # Demo mode - no backend
        response.status_code = 200
        response.headers = headers
        response.body = json.dumps({
            'response': f"Frank here. I got your message: '{message}'. To connect to Claude, set CODESPACE_URL in Vercel settings.",
            'demo': True
        })
    
    return response