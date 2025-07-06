#!/usr/bin/env python3
"""
Task Assignment Helper
Easily assign tasks to specific agents via command line
"""

import requests
import sys
import json

def assign_task(agent_id, task_description, api_base="http://127.0.0.1:5006"):
    """Assign a task to a specific agent"""
    try:
        response = requests.post(
            f"{api_base}/add_task",
            json={
                "task": task_description,
                "assigned_to": agent_id
            },
            timeout=5
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Task assigned to {agent_id}")
            print(f"📝 Task: {task_description}")
            print(f"📊 Total tasks: {result['total_tasks']}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error assigning task: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python assign_task.py <agent_id> <task_description>")
        print("Examples:")
        print("  python assign_task.py codex 'Analyze system architecture'")
        print("  python assign_task.py jules 'Monitor API health status'")
        print("  python assign_task.py claude 'Update dashboard with new metrics'")
        sys.exit(1)
    
    agent_id = sys.argv[1].lower()
    task_description = " ".join(sys.argv[2:])
    
    if agent_id not in ["codex", "jules", "claude"]:
        print(f"❌ Unknown agent: {agent_id}")
        print("Available agents: codex, jules, claude")
        sys.exit(1)
    
    assign_task(agent_id, task_description)

if __name__ == "__main__":
    main()