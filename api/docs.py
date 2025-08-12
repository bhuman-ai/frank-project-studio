from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/api/docs/<doc_name>', methods=['GET', 'OPTIONS'])
def get_document(doc_name):
    """Get document content from GitHub"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # GitHub URLs for the actual docs
    github_urls = {
        'project.md': 'https://raw.githubusercontent.com/bhuman-ai/gesture_generator/main/target-docs/project.md',
        'technical.md': 'https://raw.githubusercontent.com/bhuman-ai/gesture_generator/main/target-docs/technical.md',
        'interface.md': 'https://raw.githubusercontent.com/bhuman-ai/gesture_generator/main/target-docs/interface.md'
    }
    
    if doc_name in github_urls:
        try:
            github_response = requests.get(github_urls[doc_name])
            if github_response.status_code == 200:
                content = github_response.text
                response = jsonify({
                    'content': content,
                    'lines': len(content.split('\n'))
                })
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
        except Exception as e:
            pass
    
    # Fallback
    response = jsonify({
        'content': f"# {doc_name}\n\n*Loading...*",
        'lines': 2
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response