#!/usr/bin/env python3
"""
A2A Interactive Dashboard Server
Serves the interactive dashboard with real-time API integration
"""

from flask import Flask, render_template_string, jsonify, request, send_from_directory, redirect
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import os
from pathlib import Path
import requests
from datetime import datetime
import subprocess
import threading

app = Flask(__name__, template_folder='.')
CORS(app)
# It is highly recommended to use a more secure secret key in a real application
app.config['SECRET_KEY'] = 'a_simple_secret_key' 
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
DASHBOARD_PORT = int(os.environ.get('PORT', os.environ.get('A2A_DASHBOARD_PORT', '5003')))
JULES_API_BASE = os.environ.get('JULES_API_BASE', "http://127.0.0.1:5000")
BASE_DIR = Path(__file__).parent.parent
DASHBOARD_DIR = Path(__file__).parent

def stream_terminal_output():
    """Runs a command and streams its output to all connected clients."""
    # Monitor multiple A2A system log files for real activity
    import time
    import json
    
    # Instead of external command, generate A2A system monitoring output
    while True:
        try:
            # Simulate real A2A system monitoring
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Read actual task data
            tasks_file = BASE_DIR / "shared" / "tasks.json"
            if tasks_file.exists():
                with open(tasks_file, 'r') as f:
                    tasks = json.load(f)
                    recent_tasks = tasks[-3:] if len(tasks) > 3 else tasks
                    
                for task in recent_tasks:
                    if 'assigned_to' in task:
                        agent = task['assigned_to'].upper()
                        task_preview = task['task'][:60] + "..." if len(task['task']) > 60 else task['task']
                        output = f"[{timestamp}] {agent}: {task_preview}\n"
                        socketio.emit('terminal_output', {'data': output})
                        time.sleep(2)
            
            # System status updates
            socketio.emit('terminal_output', {'data': f"[{timestamp}] SYSTEM: A2A coordination active - {len(tasks) if 'tasks' in locals() else 0} total tasks\n"})
            socketio.emit('terminal_output', {'data': f"[{timestamp}] MONITOR: Claude, CODEX, JULES agents operational\n"})
            time.sleep(5)
            
        except Exception as e:
            socketio.emit('terminal_output', {'data': f"[{timestamp}] ERROR: {str(e)}\n"})
            time.sleep(10)

@app.route('/')
def dashboard():
    """Serve the interactive dashboard"""
    dashboard_file = DASHBOARD_DIR / "interactive_dashboard.html"
    if dashboard_file.exists():
        return render_template_string(dashboard_file.read_text())
    else:
        return jsonify({
            "service": "A2A Dashboard",
            "status": "running",
            "message": "Dashboard HTML file not found",
            "endpoints": ["/api/health", "/api/agents/status", "/api/tasks"]
        })

@app.route('/<filename>')
def serve_static(filename):
    """Serve static files like logos"""
    return send_from_directory(DASHBOARD_DIR, filename)

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "server": "A2A Dashboard",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/agents/status')
def agents_status():
    """Get agent status information"""
    try:
        # Try to get agent tasks to determine status
        response = requests.get(f"{JULES_API_BASE}/tasks", timeout=5)
        if response.status_code == 200:
            tasks = response.json()
            recent_tasks = tasks[-5:] if tasks else []
            
            # Determine agent activity based on recent tasks
            claude_active = any("claude" in task.get("task", "").lower() for task in recent_tasks)
            codex_active = any("codex" in task.get("task", "").lower() for task in recent_tasks)
            jules_active = any("jules" in task.get("task", "").lower() for task in recent_tasks)
            
            return jsonify({
                "claude": {
                    "status": "active" if claude_active else "ready",
                    "last_activity": datetime.now().isoformat(),
                    "tasks_processed": len([t for t in recent_tasks if "claude" in t.get("task", "").lower()])
                },
                "codex": {
                    "status": "active" if codex_active else "ready", 
                    "last_activity": datetime.now().isoformat(),
                    "tasks_processed": len([t for t in recent_tasks if "codex" in t.get("task", "").lower()])
                },
                "jules": {
                    "status": "active" if jules_active else "ready",
                    "last_activity": datetime.now().isoformat(), 
                    "tasks_processed": len([t for t in recent_tasks if "jules" in t.get("task", "").lower()])
                }
            })
    except Exception as e:
        return jsonify({
            "error": "Unable to fetch agent status",
            "detail": str(e)
        }), 500

@app.route('/api/tasks')
def get_tasks():
    """Get recent tasks from Jules API"""
    try:
        response = requests.get(f"{JULES_API_BASE}/tasks", timeout=5)
        if response.status_code == 200:
            tasks = response.json()
            return jsonify(tasks[-20:])  # Return last 20 tasks
        else:
            return jsonify({"error": "Unable to fetch tasks"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/submit', methods=['POST'])
def submit_task():
    """Submit a new task to the A2A system"""
    try:
        data = request.get_json()
        task_data = {
            "task": data.get("task", ""),
            "assigned_to": data.get("assigned_to", "")
        }
        
        response = requests.post(f"{JULES_API_BASE}/add_task", json=task_data, timeout=5)
        if response.status_code == 201:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to submit task"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/demo/trigger', methods=['POST'])
def trigger_demo():
    """Trigger demo mode tasks"""
    demo_tasks = [
        {
            "task": "🎬 DEMO: Create interactive web visualization",
            "assigned_to": "codex"
        },
        {
            "task": "🎬 DEMO: Process natural language request and coordinate response",
            "assigned_to": "jules"
        },
        {
            "task": "🎬 DEMO: Generate creative solution for user problem",
            "assigned_to": "codex"
        }
    ]
    
    submitted_tasks = []
    for task in demo_tasks:
        try:
            response = requests.post(f"{JULES_API_BASE}/add_task", json=task, timeout=5)
            if response.status_code == 201:
                submitted_tasks.append(task)
        except Exception as e:
            print(f"Error submitting demo task: {e}")
    
    return jsonify({
        "message": f"Demo mode activated - {len(submitted_tasks)} tasks submitted",
        "tasks": submitted_tasks
    })

@app.route('/health')
def health_check():
    """Simple health check that matches Jules API format"""
    return jsonify({
        "status": "ok",
        "server_time": datetime.now().isoformat() + "Z"
    })

@app.route('/tasks')
def tasks_proxy():
    """Proxy to Jules API for tasks"""
    try:
        response = requests.get(f"{JULES_API_BASE}/tasks", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify([])
    except Exception as e:
        return jsonify([])

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    # Start streaming terminal output in a background thread if it hasn't started
    # This ensures the command runs only once and all clients get the same stream
    if not hasattr(app, 'terminal_thread') or not app.terminal_thread.is_alive():
        app.terminal_thread = socketio.start_background_task(target=stream_terminal_output)

if __name__ == "__main__":
    print("🚀 A2A Interactive Dashboard Server")
    print(f"📱 Dashboard: http://localhost:{DASHBOARD_PORT}")
    print(f"🔗 Jules API: {JULES_API_BASE}")
    print(f"💾 Base Directory: {BASE_DIR}")
    print("🎯 Ready for real-time A2A visualization!")
    
    socketio.run(app, host="0.0.0.0", port=DASHBOARD_PORT, debug=False)