#!/usr/bin/env python3
"""
Created by: UC (Ubuntu Claude) 
Date: 2025-07-22 10:45
Purpose: Cloud version of a2a monitoring dashboard for Render
Task/Context: Deploy to a2a-system.dvo88.com
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# For cloud deployment - shows demo data when services aren't available
DEMO_MODE = os.environ.get('DEMO_MODE', 'true').lower() == 'true'

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def api_status():
    """Get current system status - demo mode for cloud"""
    if DEMO_MODE:
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'services': {
                'jules': {'status': 'demo', 'details': {'status': 'ok', 'info': 'Demo mode - connect your Jules API'}},
                'ai_connector': {'status': 'demo', 'details': {'status': 'healthy', 'info': 'Demo mode - connect your AI Connector'}},
                'redis': {'status': 'demo'},
                'dc_listener': {'status': 'stopped'},
                'ac_listener': {'status': 'stopped'}
            },
            'metrics': {
                'tasks_in_queue': 0,
                'results_processed': 0
            },
            'demo_mode': True
        })

@app.route('/api/recent-tasks')
def recent_tasks():
    """Get recent tasks - demo mode"""
    if DEMO_MODE:
        return jsonify([
            {'id': 'demo-1', 'task': 'Demo: Connect your Jules API', 'time': '10:30:00'},
            {'id': 'demo-2', 'task': 'Demo: Set REDIS_URL environment variable', 'time': '10:29:00'},
            {'id': 'demo-3', 'task': 'Demo: Deploy your services', 'time': '10:28:00'}
        ])

@app.route('/api/submit-task', methods=['POST'])
def submit_task():
    """Submit a new task - demo mode"""
    data = request.json
    task = data.get('task', '')
    
    if DEMO_MODE:
        return jsonify({
            'message': 'Demo mode - task not submitted',
            'task': task,
            'info': 'Connect your Jules API to submit real tasks'
        })

# Dashboard HTML
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>a2a System Monitor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
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
        .demo-banner {
            background: #ff9800;
            color: #000;
            padding: 10px;
            text-align: center;
            border-radius: 4px;
            margin-bottom: 20px;
            font-weight: bold;
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
        .demo { background: #ff9800; }
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
            flex-wrap: wrap;
        }
        .metric {
            text-align: center;
            min-width: 150px;
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
        .setup-guide {
            background: #333;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
        }
        .setup-guide h3 {
            color: #00D4FF;
        }
        .setup-guide code {
            background: #000;
            padding: 2px 5px;
            border-radius: 3px;
        }
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            .metrics {
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 a2a System Monitor</h1>
        
        <div id="demoBanner" class="demo-banner" style="display:none">
            DEMO MODE - Connect your services to see live data
        </div>
        
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
        
        <div class="setup-guide" id="setupGuide" style="display:none">
            <h3>🚀 Quick Setup Guide</h3>
            <p>To connect your a2a system:</p>
            <ol>
                <li>Set environment variables in Render:
                    <ul>
                        <li><code>REDIS_URL</code> - Your Redis connection URL</li>
                        <li><code>JULES_API_URL</code> - Your Jules API endpoint</li>
                        <li><code>AI_CONNECTOR_URL</code> - Your AI Connector endpoint</li>
                        <li><code>DEMO_MODE=false</code> - Disable demo mode</li>
                    </ul>
                </li>
                <li>Deploy your services (Jules, AI Connector)</li>
                <li>Refresh this page to see live data</li>
            </ol>
        </div>
    </div>
    
    <script>
        let isDemo = false;
        
        function updateStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    isDemo = data.demo_mode || false;
                    
                    // Show/hide demo banner
                    document.getElementById('demoBanner').style.display = isDemo ? 'block' : 'none';
                    document.getElementById('setupGuide').style.display = isDemo ? 'block' : 'none';
                    
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
                if (isDemo) {
                    alert('Demo Mode: ' + data.info);
                } else if (data.error) {
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
    port = int(os.environ.get('PORT', 8888))
    print(f"🚀 a2a Monitor Dashboard (Cloud) starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)