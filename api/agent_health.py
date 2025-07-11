#!/usr/bin/env python3
"""
Agent Health Monitoring System
Tracks health status of all A2A agents
"""
from flask import Flask, jsonify
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

class AgentHealthMonitor:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.health_file = self.base_dir / "shared" / "agent_health.json"
        self.agents = {
            "claude": {
                "name": "Claude",
                "type": "orchestrator",
                "health_threshold": 30,  # Context health percentage
                "last_seen": None,
                "status": "unknown",
                "context_usage": 0,
                "metrics": {}
            },
            "jules": {
                "name": "Jules", 
                "type": "api_coordinator",
                "health_threshold": 90,  # Response time threshold
                "last_seen": None,
                "status": "unknown",
                "response_time": 0,
                "metrics": {}
            },
            "codex": {
                "name": "CODEX",
                "type": "code_generator",
                "health_threshold": 95,  # Success rate threshold
                "last_seen": None,
                "status": "unknown", 
                "success_rate": 100,
                "metrics": {}
            },
            "claude_linux": {
                "name": "Claude Linux",
                "type": "system_operator",
                "health_threshold": 30,  # Context health percentage
                "last_seen": None,
                "status": "unknown",
                "context_usage": 0,
                "metrics": {}
            }
        }
        self.load_health_data()
    
    def load_health_data(self):
        """Load saved health data"""
        if self.health_file.exists():
            try:
                with open(self.health_file, 'r') as f:
                    saved_data = json.load(f)
                    for agent_id, data in saved_data.items():
                        if agent_id in self.agents:
                            self.agents[agent_id].update(data)
            except:
                pass
    
    def save_health_data(self):
        """Save health data to file"""
        self.health_file.parent.mkdir(exist_ok=True)
        with open(self.health_file, 'w') as f:
            json.dump(self.agents, f, indent=2, default=str)
    
    def update_agent_health(self, agent_id, health_data):
        """Update health status for an agent"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        agent["last_seen"] = datetime.utcnow().isoformat() + "Z"
        
        # Update metrics based on agent type
        if "context_usage" in health_data:
            agent["context_usage"] = health_data["context_usage"]
            # Determine health based on context usage
            if agent["context_usage"] < 30:
                agent["status"] = "healthy"
            elif agent["context_usage"] < 70:
                agent["status"] = "warning"
            else:
                agent["status"] = "critical"
        
        if "response_time" in health_data:
            agent["response_time"] = health_data["response_time"]
            agent["status"] = "healthy" if agent["response_time"] < 1000 else "warning"
        
        if "success_rate" in health_data:
            agent["success_rate"] = health_data["success_rate"]
            agent["status"] = "healthy" if agent["success_rate"] > 95 else "warning"
        
        if "tasks_processed" in health_data:
            agent["metrics"]["tasks_processed"] = health_data.get("tasks_processed", 0)
        
        self.save_health_data()
        return True
    
    def check_agent_status(self, agent_id):
        """Check if agent is responsive"""
        if agent_id not in self.agents:
            return "unknown"
        
        agent = self.agents[agent_id]
        if not agent["last_seen"]:
            return "offline"
        
        # Check if agent was seen in last 5 minutes
        last_seen = datetime.fromisoformat(agent["last_seen"].replace('Z', '+00:00'))
        time_since = datetime.utcnow() - last_seen.replace(tzinfo=None)
        
        if time_since > timedelta(minutes=5):
            agent["status"] = "offline"
        
        return agent["status"]
    
    def get_all_health_status(self):
        """Get health status for all agents"""
        health_report = {}
        for agent_id, agent in self.agents.items():
            status = self.check_agent_status(agent_id)
            health_report[agent_id] = {
                "name": agent["name"],
                "type": agent["type"],
                "status": status,
                "last_seen": agent["last_seen"],
                "context_usage": agent.get("context_usage", 0),
                "response_time": agent.get("response_time", 0),
                "success_rate": agent.get("success_rate", 100),
                "metrics": agent.get("metrics", {})
            }
        return health_report
    
    def get_health_summary(self):
        """Get a summary of system health"""
        all_health = self.get_all_health_status()
        
        total_agents = len(self.agents)
        healthy_agents = sum(1 for a in all_health.values() if a["status"] == "healthy")
        warning_agents = sum(1 for a in all_health.values() if a["status"] == "warning")
        critical_agents = sum(1 for a in all_health.values() if a["status"] == "critical")
        offline_agents = sum(1 for a in all_health.values() if a["status"] in ["offline", "unknown"])
        
        return {
            "total_agents": total_agents,
            "healthy": healthy_agents,
            "warning": warning_agents,
            "critical": critical_agents,
            "offline": offline_agents,
            "system_status": "healthy" if healthy_agents == total_agents else "degraded",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

# Flask endpoints for agent health
def create_health_endpoints(app):
    monitor = AgentHealthMonitor()
    
    @app.route("/api/agents/health")
    def get_agents_health():
        """Get health status for all agents"""
        return jsonify(monitor.get_all_health_status())
    
    @app.route("/api/agents/health/summary")
    def get_health_summary():
        """Get system health summary"""
        return jsonify(monitor.get_health_summary())
    
    @app.route("/api/agents/<agent_id>/health", methods=["POST"])
    def update_agent_health(agent_id):
        """Update health data for a specific agent"""
        from flask import request
        health_data = request.get_json()
        success = monitor.update_agent_health(agent_id, health_data)
        if success:
            return jsonify({"status": "updated", "agent": agent_id})
        else:
            return jsonify({"error": "Unknown agent"}), 404
    
    return monitor