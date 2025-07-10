#!/usr/bin/env python3
"""
Real-time A2A Task Monitor
Shows latest tasks and agent responses
"""

import requests
import json
import time
from datetime import datetime
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_tasks():
    try:
        response = requests.get('http://127.0.0.1:5003/tasks')
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def display_tasks(tasks, num_recent=10):
    clear_screen()
    print("=" * 80)
    print(f"🤖 A2A TASK MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Get recent tasks
    recent_tasks = tasks[-num_recent:] if len(tasks) > num_recent else tasks
    
    print(f"\n📊 Total Tasks: {len(tasks)} | Showing last {len(recent_tasks)}")
    print("-" * 80)
    
    for task in recent_tasks:
        created = task.get('created', 'Unknown')
        assigned_to = task.get('assigned_to', 'all')
        task_text = task.get('task', '')
        
        # Color code by agent
        agent_emoji = {
            'codex': '🧠',
            'jules': '⚡',
            'all': '🌐',
            'claude': '🤖'
        }.get(assigned_to.lower(), '📌')
        
        # Truncate long tasks
        if len(task_text) > 100:
            task_text = task_text[:97] + '...'
        
        print(f"\n{agent_emoji} [{created}] → {assigned_to.upper()}")
        print(f"   {task_text}")
    
    print("\n" + "=" * 80)
    print("Press Ctrl+C to exit | Updates every 5 seconds")

def main():
    print("Starting A2A Task Monitor...")
    
    try:
        while True:
            tasks = get_tasks()
            if tasks:
                display_tasks(tasks)
            else:
                print("⚠️  Could not fetch tasks. Is Jules server running on port 5003?")
            
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped.")

if __name__ == "__main__":
    main()