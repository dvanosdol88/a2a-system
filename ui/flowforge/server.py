#!/usr/bin/env python3
"""
FlowForge UI Server
Serves the FlowForge user-friendly interface on port 5002
"""

from flask import Flask, send_from_directory, jsonify
import os
from pathlib import Path

app = Flask(__name__)

# Get the directory containing this script
BASE_DIR = Path(__file__).parent

@app.route('/')
def index():
    """Serve the main FlowForge interface"""
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/styles.css')
def styles():
    """Serve the FlowForge CSS"""
    return send_from_directory(BASE_DIR, 'styles.css')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "flowforge_ui",
        "message": "FlowForge UI server is running"
    })

@app.route('/api/status')
def api_status():
    """Provide status information for the FlowForge UI"""
    return jsonify({
        "ui_version": "1.0.0",
        "brand": "FlowForge",
        "api_base": "http://127.0.0.1:5000",
        "dashboard_url": "http://127.0.0.1:5001",
        "features": [
            "Task Submission Interface",
            "Real-time Agent Status",
            "GitHub Integration Status",
            "Live Activity Feed",
            "FlowForge Branding"
        ]
    })

if __name__ == '__main__':
    print("🎨 FlowForge UI Server")
    print("=" * 40)
    print("🚀 Starting FlowForge interface on http://127.0.0.1:5002")
    print("📱 User-friendly AI agent collaboration platform")
    print("🎯 Option #3: Minimal Dashboard Design")
    print()
    print("Features:")
    print("  ✅ Task submission interface")
    print("  ✅ Real-time system status")
    print("  ✅ Live activity feed")
    print("  ✅ FlowForge brand styling")
    print("  ✅ Responsive design")
    print()
    print("Press Ctrl+C to stop...")
    
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=False
    )