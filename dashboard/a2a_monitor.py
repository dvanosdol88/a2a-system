#!/usr/bin/env python3
"""
Created by: UC (Ubuntu Claude) 
Date: 2025-07-22 10:35
Purpose: Simple a2a monitoring dashboard server
Task/Context: Quick dashboard to monitor agents and give directions
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import subprocess
import json
import redis
import requests
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Redis connection
import os
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
JULES_API_URL = os.environ.get('JULES_API_URL', 'http://localhost:5000')
AI_CONNECTOR_URL = os.environ.get('AI_CONNECTOR_URL', 'http://localhost:8080')

try:
    if REDIS_URL.startswith('redis://'):
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    else:
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
except:
    redis_client = None

def check_service_health(name, url):
    """Check if a service is healthy"""
    try:
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            return {
                'status': 'running',
                'details': data
            }
    except:
        pass
    return {'status': 'stopped', 'details': {}}

def get_process_status(process_name):
    """Check if a process is running"""
    try:
        result = subprocess.run(['pgrep', '-f', process_name], 
                              capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except:
        return False

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def api_status():
    """Get current system status"""
    # Check services
    jules_health = check_service_health('Jules API', f'{JULES_API_URL}/health')
    ai_connector_health = check_service_health('AI Connector', f'{AI_CONNECTOR_URL}/health')
    
    # Check Redis
    redis_status = 'running' if redis_client and redis_client.ping() else 'stopped'
    
    # Get task counts
    task_count = 0
    result_count = 0
    if redis_client:
        try:
            task_count = redis_client.xlen('a2a_stream')
            result_count = redis_client.xlen('a2a_stream_results')
        except:
            pass
    
    # Check listeners
    dc_listening = get_process_status('dc_listener')
    ac_listening = get_process_status('ac_listener')
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'services': {
            'jules': jules_health,
            'ai_connector': ai_connector_health,
            'redis': {'status': redis_status},
            'dc_listener': {'status': 'running' if dc_listening else 'stopped'},
            'ac_listener': {'status': 'running' if ac_listening else 'stopped'}
        },
        'metrics': {
            'tasks_in_queue': task_count,
            'results_processed': result_count
        }
    })

@app.route('/api/recent-tasks')
def recent_tasks():
    """Get recent tasks from Redis"""
    tasks = []
    if redis_client:
        try:
            # Get last 10 tasks
            stream_data = redis_client.xrevrange('a2a_stream', count=10)
            for msg_id, data in stream_data:
                timestamp = datetime.fromtimestamp(int(msg_id.split('-')[0]) / 1000)
                tasks.append({
                    'id': msg_id,
                    'task': data.get('task', 'Unknown'),
                    'time': timestamp.strftime('%H:%M:%S')
                })
        except:
            pass
    return jsonify(tasks)

@app.route('/api/submit-task', methods=['POST'])
def submit_task():
    """Submit a new task"""
    data = request.json
    task = data.get('task', '')
    
    if not task:
        return jsonify({'error': 'No task provided'}), 400
    
    try:
        # Submit to Jules API
        resp = requests.post(f'{JULES_API_URL}/add_task', 
                           json={'task': task})
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard HTML
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>a2a System Monitor</title>
    <style>
        body {
            font-family: -apple-system, Arial, sans-serif;
            background: #1a1a1a;
            color: #fff;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #00D4FF;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 20px;
        }
        .service {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .status {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .running { background: #4CAF50; }
        .stopped { background: #f44336; }
        .task-input {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input {
            flex: 1;
            padding: 10px;
            background: #333;
            border: 1px solid #555;
            color: #fff;
            border-radius: 4px;
        }
        button {
            padding: 10px 20px;
            background: #00D4FF;
            color: #000;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background: #00a8cc;
        }
        .tasks {
            max-height: 300px;
            overflow-y: auto;
        }
        .task-item {
            padding: 10px;
            background: #333;
            margin-bottom: 5px;
            border-radius: 4px;
            font-size: 14px;
        }
        .metrics {
            display: flex;
            gap: 30px;
            margin-bottom: 20px;
        }
        .metric {
            text-align: center;
        }
        .metric-value {
            font-size: 36px;
            color: #00D4FF;
            font-weight: bold;
        }
        .metric-label {
            color: #888;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 a2a System Monitor</h1>
        
        <div class="task-input">
            <input type="text" id="taskInput" placeholder="Enter task description..." />
            <button onclick="submitTask()">Submit Task</button>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value" id="taskCount">-</div>
                <div class="metric-label">Tasks in Queue</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="resultCount">-</div>
                <div class="metric-label">Results Processed</div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Services</h3>
                <div id="services"></div>
            </div>
            
            <div class="card">
                <h3>Recent Tasks</h3>
                <div class="tasks" id="tasks"></div>
            </div>
        </div>
    </div>
    
    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    // Update metrics
                    document.getElementById('taskCount').textContent = data.metrics.tasks_in_queue;
                    document.getElementById('resultCount').textContent = data.metrics.results_processed;
                    
                    // Update services
                    const servicesHtml = Object.entries(data.services).map(([name, info]) => {
                        const status = info.status;
                        return `<div class="service">
                            <span><span class="status ${status}"></span>${name}</span>
                            <span>${status}</span>
                        </div>`;
                    }).join('');
                    document.getElementById('services').innerHTML = servicesHtml;
                });
            
            // Update tasks
            fetch('/api/recent-tasks')
                .then(r => r.json())
                .then(tasks => {
                    const tasksHtml = tasks.map(t => 
                        `<div class="task-item">${t.time} - ${t.task}</div>`
                    ).join('');
                    document.getElementById('tasks').innerHTML = tasksHtml || '<div class="task-item">No recent tasks</div>';
                });
        }
        
        function submitTask() {
            const input = document.getElementById('taskInput');
            const task = input.value.trim();
            if (!task) return;
            
            fetch('/api/submit-task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task: task})
            })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    input.value = '';
                    updateStatus();
                }
            });
        }
        
        // Update every 2 seconds
        setInterval(updateStatus, 2000);
        updateStatus();
        
        // Submit on Enter
        document.getElementById('taskInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') submitTask();
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 a2a Monitor Dashboard starting on http://localhost:8888")
    app.run(host='0.0.0.0', port=8888, debug=False)