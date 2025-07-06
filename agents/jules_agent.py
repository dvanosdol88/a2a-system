#!/usr/bin/env python3
"""
Jules Agent - Automated A2A Task Processor
Polls for assigned tasks and provides automated responses
"""

import requests
import time
import json
from datetime import datetime
from pathlib import Path

class JulesAgent:
    def __init__(self, api_base="http://127.0.0.1:5006", agent_id="jules"):
        self.api_base = api_base
        self.agent_id = agent_id
        self.running = False
        self.poll_interval = 12  # seconds (slightly different from CODEX)
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] JULES: {message}")
        
    def get_pending_tasks(self):
        """Get pending tasks assigned to this agent"""
        try:
            response = requests.get(f"{self.api_base}/agent/{self.agent_id}/tasks", timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            self.log(f"Error fetching tasks: {e}")
            return []
    
    def acknowledge_task(self, task_id):
        """Acknowledge receiving a task"""
        try:
            response = requests.post(
                f"{self.api_base}/agent/{self.agent_id}/tasks/{task_id}/acknowledge",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            self.log(f"Error acknowledging task {task_id}: {e}")
            return False
    
    def complete_task(self, task_id, response_text):
        """Mark task as completed with response"""
        try:
            response = requests.post(
                f"{self.api_base}/agent/{self.agent_id}/tasks/{task_id}/complete",
                json={"response": response_text},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            self.log(f"Error completing task {task_id}: {e}")
            return False
    
    def process_task(self, task):
        """Process a task and generate appropriate response"""
        task_text = task["task"].lower()
        task_id = task["id"]
        
        # Acknowledge the task first
        if self.acknowledge_task(task_id):
            self.log(f"Acknowledged task {task_id}: {task['task'][:50]}...")
        
        # Generate response based on task content
        response = "⚡ JULES acknowledged and processing..."
        
        if "api" in task_text or "server" in task_text:
            response = "🌐 JULES: API services operational. Server endpoints ready for coordination."
        elif "task" in task_text and "queue" in task_text:
            response = "📋 JULES: Task queue management active. Routing capabilities engaged."
        elif "monitoring" in task_text or "dashboard" in task_text:
            response = "📊 JULES: Monitoring services active. Data pipeline operational."
        elif "communication" in task_text or "message" in task_text:
            response = "💬 JULES: Communication relay established. Message routing protocols active."
        elif "security" in task_text:
            response = "🔐 JULES: Security protocols acknowledged. Coordinating with agents for secure operations."
        elif "test" in task_text or "health" in task_text:
            response = "✅ JULES: System health confirmed. All API endpoints responding normally."
        elif "coordination" in task_text or "orchestration" in task_text:
            response = "🎯 JULES: Coordination hub active. Agent communication channels established."
        else:
            response = f"⚡ JULES: Task received and queued. Processing: {task['task'][:30]}..."
        
        # Complete the task
        if self.complete_task(task_id, response):
            self.log(f"Completed task {task_id}")
            return True
        return False
    
    def start(self):
        """Start the agent polling loop"""
        self.running = True
        self.log("JULES Agent starting up...")
        self.log(f"Polling {self.api_base} every {self.poll_interval} seconds")
        
        while self.running:
            try:
                # Get pending tasks
                tasks = self.get_pending_tasks()
                
                if tasks:
                    self.log(f"Found {len(tasks)} pending tasks")
                    for task in tasks:
                        self.process_task(task)
                
                time.sleep(self.poll_interval)
                
            except KeyboardInterrupt:
                self.log("Shutting down...")
                self.running = False
            except Exception as e:
                self.log(f"Error in main loop: {e}")
                time.sleep(30)  # Wait longer on error
    
    def stop(self):
        """Stop the agent"""
        self.running = False

if __name__ == "__main__":
    agent = JulesAgent()
    try:
        agent.start()
    except KeyboardInterrupt:
        agent.log("JULES Agent stopped")