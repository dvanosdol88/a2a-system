#!/usr/bin/env python3
"""
Claude-to-Jules Communication Helper
Created: 2025-07-04
Purpose: Utility functions for Claude to communicate with Jules API
"""

import requests
import json
from typing import Dict, List, Optional
from pathlib import Path

class JulesAPIClient:
    """Client for communicating with Jules API server"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def health_check(self) -> Dict:
        """Check if Jules API server is running"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def add_task(self, task: str) -> Dict:
        """Add a task to Jules queue"""
        try:
            data = {"task": task}
            response = self.session.post(
                f"{self.base_url}/add_task",
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to add task: {e}"}
    
    def list_tasks(self) -> List[Dict]:
        """List all tasks in Jules queue"""
        try:
            response = self.session.get(f"{self.base_url}/tasks", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return [{"error": f"Failed to list tasks: {e}"}]
    
    def send_message_to_jules(self, message: str, task_type: str = "message") -> Dict:
        """Send a message to Jules via task queue"""
        formatted_task = f"[{task_type}] {message}"
        return self.add_task(formatted_task)
    
    def get_task_count(self) -> int:
        """Get the number of tasks in the queue"""
        tasks = self.list_tasks()
        return len(tasks) if not any("error" in task for task in tasks) else 0
    
    def is_server_running(self) -> bool:
        """Check if Jules API server is accessible"""
        health = self.health_check()
        return health.get("status") == "ok"

# Convenience functions for direct use
def send_to_jules(message: str, task_type: str = "message") -> Dict:
    """Send message to Jules - convenience function"""
    client = JulesAPIClient()
    return client.send_message_to_jules(message, task_type)

def check_jules_status() -> Dict:
    """Check Jules API status - convenience function"""
    client = JulesAPIClient()
    return client.health_check()

def get_jules_tasks() -> List[Dict]:
    """Get all Jules tasks - convenience function"""
    client = JulesAPIClient()
    return client.list_tasks()

if __name__ == "__main__":
    # Test the communication
    client = JulesAPIClient()
    
    print("Testing Jules API communication...")
    
    # Health check
    health = client.health_check()
    print(f"Health check: {health}")
    
    if health.get("status") == "ok":
        # Send test message
        result = client.send_message_to_jules("Hello from Claude!", "test")
        print(f"Message sent: {result}")
        
        # List tasks
        tasks = client.list_tasks()
        print(f"Current tasks: {json.dumps(tasks, indent=2)}")
        
        print("✅ Jules API communication test successful!")
    else:
        print("❌ Jules API server not available")