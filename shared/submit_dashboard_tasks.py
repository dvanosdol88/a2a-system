#!/usr/bin/env python3
"""
Submit dashboard enhancement tasks to CODEX and JULES agents
"""

import requests
import json
from datetime import datetime

def submit_tasks():
    """Submit interactive dashboard tasks to both agents"""
    
    # Task for CODEX to enhance with web development capabilities
    codex_task = {
        "task": "A2A INTERACTIVE DASHBOARD: Create stunning real-time visualization dashboard showing User→Claude→CODEX→JULES message flow. Features: 1) Animated agent icons with working states, 2) Real-time message flow visualization, 3) Demo mode button, 4) Professional UI with smooth animations. Make it visually impressive for non-technical users!",
        "assigned_to": "codex"
    }
    
    # Task for JULES to enhance API capabilities
    jules_task = {
        "task": "A2A DASHBOARD API: Enhance Jules server with real-time dashboard endpoints. Add: 1) /dashboard/agents/status - agent health/activity, 2) /dashboard/messages/flow - message flow data, 3) /dashboard/demo - demo mode triggers, 4) WebSocket support for real-time updates. Coordinate with CODEX for seamless integration.",
        "assigned_to": "jules"
    }
    
    results = []
    
    try:
        # Submit CODEX task
        response = requests.post('http://127.0.0.1:5000/add_task', json=codex_task, timeout=5)
        results.append(f"CODEX task: {response.status_code} - {response.json()}")
        
        # Submit JULES task
        response = requests.post('http://127.0.0.1:5000/add_task', json=jules_task, timeout=5)
        results.append(f"JULES task: {response.status_code} - {response.json()}")
        
    except Exception as e:
        results.append(f"Error: {e}")
    
    return results

if __name__ == "__main__":
    print("🚀 Submitting A2A Interactive Dashboard Tasks...")
    results = submit_tasks()
    for result in results:
        print(result)
    print("✅ Tasks submitted to agents!")