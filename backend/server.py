#!/usr/bin/env python3
"""
Frank Project Studio - Backend Server
Runs in GitHub Codespace to handle Claude CLI calls
"""

import os
import sys
import subprocess
import json
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins for Codespace

# Configuration - Support multiple projects
DEFAULT_PROJECT = os.environ.get('PROJECT_DIR', '/workspaces/AI-Video-Studio')
# Try common project locations
if not os.path.exists(DEFAULT_PROJECT):
    if os.path.exists('/workspaces/AI-Video-Studio'):
        DEFAULT_PROJECT = '/workspaces/AI-Video-Studio'
    elif os.path.exists('/Users/don/AI Video Studio'):
        DEFAULT_PROJECT = '/Users/don/AI Video Studio'
    else:
        DEFAULT_PROJECT = os.getcwd()

PROJECT_DIR = DEFAULT_PROJECT
BLUEPRINT_DIR = os.path.join(PROJECT_DIR, 'target-docs')

# Ensure directories exist
os.makedirs(BLUEPRINT_DIR, exist_ok=True)

# Global state
conversation_context = ""
doc_version = 1

def call_claude(prompt, max_tokens=2000):
    """Call Claude CLI and return response"""
    try:
        # Try to use claude CLI
        result = subprocess.run(
            ['claude', '--dangerously-skip-permissions', '--print'],
            input=prompt[:8000],  # Limit prompt size
            text=True,
            capture_output=True,
            timeout=30,
            cwd=PROJECT_DIR
        )
        
        response = result.stdout.strip()
        if response:
            return response[:max_tokens]
        else:
            return "Claude didn't respond. Check CLI is working: claude --version"
            
    except subprocess.TimeoutExpired:
        return "Claude is taking longer than expected..."
    except FileNotFoundError:
        return """Claude CLI not found. Install it:
        
Option 1: npm install -g @anthropic/claude-cli
Option 2: pip install anthropic-claude-cli

Then authenticate: claude auth"""
    except Exception as e:
        return f"Error calling Claude: {str(e)}"

def init_blueprint_docs():
    """Initialize blueprint documents if they don't exist"""
    docs = {
        'project.md': """# Project Blueprint

## Vision
*Your project vision will be discovered through our conversation...*

## Current State
*Analyzing your existing code...*

## Target Features
*We'll define these together...*

## User Stories
*Coming soon as we understand your users...*
""",
        'technical.md': """# Technical Blueprint

## Architecture
*Understanding your technical needs...*

## Tech Stack
*Detecting from your project...*

## API Design
*Will be defined as we discuss...*

## Database Schema
*Taking shape through our conversation...*
""",
        'interface.md': """# Interface Blueprint

## User Experience
*Exploring the best UX for your users...*

## Screens & Flows
*Defining through our discussion...*

## Components
*Will emerge from your requirements...*

## Design System
*Crafting as we understand your brand...*
"""
    }
    
    for filename, content in docs.items():
        filepath = os.path.join(BLUEPRINT_DIR, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Initialized {filename}")

def update_document(doc_name, new_content):
    """Update a blueprint document by ADDING content"""
    doc_path = os.path.join(BLUEPRINT_DIR, doc_name)
    
    # Read current content
    current_content = ""
    if os.path.exists(doc_path):
        with open(doc_path, 'r') as f:
            current_content = f.read()
    
    # Create merge prompt
    prompt = f"""You must ADD content to the existing document. DO NOT replace it.

CURRENT FULL DOCUMENT {doc_name}:
{current_content}

NEW INFORMATION TO ADD:
{new_content}

INSTRUCTIONS:
1. Output the COMPLETE document
2. Keep ALL existing content
3. ADD new information to appropriate sections
4. If a section exists, EXPAND it (don't replace)
5. If a section is new, ADD it

Output the FULL merged document with both old and new content."""

    # Get merged document
    merged = call_claude(prompt, max_tokens=10000)
    
    # Save updated document
    with open(doc_path, 'w') as f:
        f.write(merged)
    
    return len(merged.split('\n'))

@app.route('/health')
def health():
    """Health check endpoint"""
    # Check if Claude CLI is available
    try:
        result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
        claude_available = bool(result.stdout.strip())
    except:
        claude_available = False
    
    return jsonify({
        'status': 'healthy',
        'project': PROJECT_DIR,
        'blueprint_dir': BLUEPRINT_DIR,
        'claude': claude_available,
        'version': doc_version
    })

@app.route('/api/message', methods=['POST', 'OPTIONS'])
def handle_message():
    """Handle chat message from frontend"""
    if request.method == 'OPTIONS':
        return '', 200
    
    global conversation_context, doc_version
    
    data = request.json
    user_message = data.get('message', '')
    context = data.get('context', '')
    
    # Build prompt for Frank
    prompt = f"""You are Uncle Frank, a no-nonsense technical advisor from Brooklyn who helps people build great software.

Recent conversation:
{conversation_context[-1500:]}

User just said: {user_message}

Respond naturally as Frank. Be direct, practical, cut through the BS. Help them understand what they need to build.

AS YOU LEARN THINGS, identify what should be added to the blueprint docs.

Format your response:
[Your conversational response as Frank]

[DOC-UPDATES]
PROJECT.MD:
[Specific things to add about vision, features, or requirements - or leave blank]

TECHNICAL.MD:
[Specific technical decisions or architecture notes - or leave blank]

INTERFACE.MD:
[Specific UI/UX insights - or leave blank]
[END-DOC-UPDATES]"""

    # Get Frank's response
    response = call_claude(prompt)
    
    # Parse response
    conversation = response
    doc_updates = {}
    
    if '[DOC-UPDATES]' in response and '[END-DOC-UPDATES]' in response:
        parts = response.split('[DOC-UPDATES]')
        conversation = parts[0].strip()
        
        doc_section = parts[1].split('[END-DOC-UPDATES]')[0]
        
        # Extract updates for each doc
        for doc_type in ['PROJECT', 'TECHNICAL', 'INTERFACE']:
            pattern = f"{doc_type}.MD:"
            if pattern in doc_section:
                content = doc_section.split(pattern)[1]
                # Find next section or end
                for next_pattern in ['PROJECT.MD:', 'TECHNICAL.MD:', 'INTERFACE.MD:']:
                    if next_pattern != pattern and next_pattern in content:
                        content = content.split(next_pattern)[0]
                        break
                
                content = content.strip()
                if content and len(content) > 10:  # Only if there's real content
                    doc_updates[doc_type.lower()] = content
    
    # Update documents in background
    if doc_updates:
        def update_docs():
            for doc_type, content in doc_updates.items():
                try:
                    lines = update_document(f'{doc_type}.md', content)
                    print(f"Updated {doc_type}.md ({lines} lines)")
                except Exception as e:
                    print(f"Error updating {doc_type}.md: {e}")
        
        threading.Thread(target=update_docs).start()
    
    # Update context
    conversation_context += f"\nUser: {user_message}\nFrank: {conversation[:200]}"
    if len(conversation_context) > 3000:
        conversation_context = conversation_context[-3000:]
    
    doc_version += 1
    
    return jsonify({
        'response': conversation,
        'doc_updates': doc_updates if doc_updates else None,
        'version': doc_version
    })

@app.route('/api/docs/<doc_name>')
def get_document(doc_name):
    """Get document content"""
    if not doc_name.endswith('.md'):
        doc_name = doc_name + '.md'
    
    doc_path = os.path.join(BLUEPRINT_DIR, doc_name)
    
    if not os.path.exists(doc_path):
        init_blueprint_docs()
    
    try:
        with open(doc_path, 'r') as f:
            content = f.read()
        
        return jsonify({
            'content': content,
            'lines': len(content.split('\n')),
            'path': doc_path
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'content': f"# {doc_name}\n\nError loading document.",
            'lines': 2
        })

@app.route('/api/project', methods=['POST', 'OPTIONS'])
def switch_project():
    """Clone/switch to a different GitHub project"""
    if request.method == 'OPTIONS':
        return '', 200
    
    global PROJECT_DIR, BLUEPRINT_DIR
    
    data = request.json
    github_url = data.get('github_url', '')
    
    if not github_url:
        return jsonify({'success': False, 'error': 'No GitHub URL provided'})
    
    # Extract repo info from URL
    # Handle formats: https://github.com/user/repo or https://github.com/user/repo.git
    url_parts = github_url.replace('.git', '').rstrip('/').split('/')
    repo_name = url_parts[-1]
    user_name = url_parts[-2] if len(url_parts) > 1 else 'unknown'
    
    # Clone location
    clone_dir = f"/workspaces/{user_name}-{repo_name}"
    
    try:
        # Check if already cloned
        if not os.path.exists(clone_dir):
            print(f"Cloning {github_url} to {clone_dir}...")
            
            # Clone the repo
            result = subprocess.run(
                ['git', 'clone', github_url, clone_dir],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return jsonify({
                    'success': False,
                    'error': f"Clone failed: {result.stderr}"
                })
            
            print(f"Successfully cloned to {clone_dir}")
        else:
            print(f"Project already exists at {clone_dir}, pulling latest...")
            # Pull latest changes
            subprocess.run(
                ['git', 'pull'],
                cwd=clone_dir,
                capture_output=True,
                timeout=30
            )
        
        # Update project directory
        PROJECT_DIR = clone_dir
        BLUEPRINT_DIR = os.path.join(PROJECT_DIR, 'target-docs')
        os.makedirs(BLUEPRINT_DIR, exist_ok=True)
        
        # Initialize blueprint docs for new project
        init_blueprint_docs()
        
        # Count files
        file_count = 0
        for root, dirs, files in os.walk(PROJECT_DIR):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            file_count += len(files)
        
        return jsonify({
            'success': True,
            'name': f"{user_name}/{repo_name}",
            'path': clone_dir,
            'file_count': file_count,
            'status': 'Ready to build',
            'blueprint_dir': BLUEPRINT_DIR
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Clone timeout - repository may be too large'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/analyze')
def analyze_project():
    """Analyze project structure"""
    try:
        # Count files
        file_count = 0
        for root, dirs, files in os.walk(PROJECT_DIR):
            # Skip hidden and node_modules
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            file_count += len(files)
        
        # Detect tech stack
        stack = []
        if os.path.exists(os.path.join(PROJECT_DIR, 'package.json')):
            stack.append('Node.js/JavaScript')
        if os.path.exists(os.path.join(PROJECT_DIR, 'requirements.txt')):
            stack.append('Python')
        if os.path.exists(os.path.join(PROJECT_DIR, 'Gemfile')):
            stack.append('Ruby')
        if os.path.exists(os.path.join(PROJECT_DIR, 'go.mod')):
            stack.append('Go')
        if os.path.exists(os.path.join(PROJECT_DIR, 'Cargo.toml')):
            stack.append('Rust')
        
        # Get main directories
        dirs = [d for d in os.listdir(PROJECT_DIR) 
                if os.path.isdir(os.path.join(PROJECT_DIR, d)) 
                and not d.startswith('.') 
                and d != 'node_modules'][:10]
        
        return jsonify({
            'file_count': file_count,
            'stack': stack,
            'directories': dirs,
            'project_dir': PROJECT_DIR
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("=" * 60)
    print("🎩 FRANK PROJECT STUDIO - BACKEND SERVER")
    print("=" * 60)
    print(f"Project: {PROJECT_DIR}")
    print(f"Blueprints: {BLUEPRINT_DIR}")
    print("=" * 60)
    
    # Initialize documents
    init_blueprint_docs()
    print("Blueprint documents initialized")
    print("=" * 60)
    
    # Check Claude CLI
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        print(f"✅ Claude CLI: {result.stdout.strip()}")
    except:
        print("⚠️  Claude CLI not found. Install it:")
        print("   npm install -g @anthropic/claude-cli")
        print("   OR")
        print("   pip install anthropic-claude-cli")
    
    print("=" * 60)
    print("")
    print("🚀 Starting server on port 8080...")
    print("")
    print("Your Codespace URL for Vercel:")
    codespace_name = os.environ.get('CODESPACE_NAME', 'your-codespace-name')
    print(f"https://{codespace_name}-8080.preview.app.github.dev")
    print("")
    print("Set this as CODESPACE_URL in your Vercel environment")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8080, debug=True)