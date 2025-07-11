#!/usr/bin/env python3
"""
Project Management for A2A System
Tracks multiple simultaneous projects and their outputs
"""
from datetime import datetime
import json
import uuid
from pathlib import Path

class ProjectManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.projects_file = self.base_dir / "shared" / "projects.json"
        self.projects = {}
        self.load_projects()
    
    def load_projects(self):
        """Load existing projects from file"""
        if self.projects_file.exists():
            try:
                with open(self.projects_file, 'r') as f:
                    self.projects = json.load(f)
            except:
                self.projects = {}
    
    def save_projects(self):
        """Save projects to file"""
        self.projects_file.parent.mkdir(exist_ok=True)
        with open(self.projects_file, 'w') as f:
            json.dump(self.projects, f, indent=2, default=str)
    
    def create_project(self, name, description, assigned_agents):
        """Create a new project"""
        project_id = str(uuid.uuid4())[:8]
        
        project = {
            "id": project_id,
            "name": name,
            "description": description,
            "assigned_agents": assigned_agents,
            "status": "active",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "activities": [],
            "output": None,
            "completion_percentage": 0
        }
        
        self.projects[project_id] = project
        self.save_projects()
        return project_id
    
    def add_activity(self, project_id, agent, action, details=None):
        """Add an activity to a project"""
        if project_id not in self.projects:
            return False
        
        activity = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent": agent,
            "action": action,
            "details": details
        }
        
        self.projects[project_id]["activities"].append(activity)
        self.projects[project_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self.save_projects()
        return True
    
    def update_project_status(self, project_id, status, completion_percentage=None):
        """Update project status"""
        if project_id not in self.projects:
            return False
        
        self.projects[project_id]["status"] = status
        if completion_percentage is not None:
            self.projects[project_id]["completion_percentage"] = completion_percentage
        
        self.projects[project_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self.save_projects()
        return True
    
    def set_project_output(self, project_id, output):
        """Set the final output for a project"""
        if project_id not in self.projects:
            return False
        
        self.projects[project_id]["output"] = output
        self.projects[project_id]["status"] = "completed"
        self.projects[project_id]["completion_percentage"] = 100
        self.projects[project_id]["completed_at"] = datetime.utcnow().isoformat() + "Z"
        self.save_projects()
        return True
    
    def get_project(self, project_id):
        """Get a specific project"""
        return self.projects.get(project_id)
    
    def get_active_projects(self):
        """Get all active projects"""
        return {
            pid: proj for pid, proj in self.projects.items() 
            if proj["status"] == "active"
        }
    
    def get_recent_activities(self, project_id, limit=20):
        """Get recent activities for a project"""
        if project_id not in self.projects:
            return []
        
        activities = self.projects[project_id]["activities"]
        return activities[-limit:] if len(activities) > limit else activities
    
    def get_agent_summary(self, project_id, agent_name):
        """Get a summary of what an agent did in a project"""
        if project_id not in self.projects:
            return {}
        
        activities = [
            act for act in self.projects[project_id]["activities"]
            if act["agent"] == agent_name
        ]
        
        return {
            "agent": agent_name,
            "total_actions": len(activities),
            "actions": activities,
            "first_action": activities[0]["timestamp"] if activities else None,
            "last_action": activities[-1]["timestamp"] if activities else None
        }

def create_project_endpoints(app, socketio):
    """Create Flask endpoints for project management"""
    from flask import request, jsonify
    manager = ProjectManager()
    
    @app.route("/api/projects", methods=["POST"])
    def create_project():
        """Create a new project"""
        data = request.get_json()
        project_id = manager.create_project(
            name=data.get("name", "Untitled Project"),
            description=data.get("description", ""),
            assigned_agents=data.get("assigned_agents", [])
        )
        
        # Emit project creation event
        socketio.emit('project_created', {
            'project_id': project_id,
            'project': manager.get_project(project_id)
        })
        
        return jsonify({"project_id": project_id})
    
    @app.route("/api/projects/<project_id>")
    def get_project(project_id):
        """Get project details"""
        project = manager.get_project(project_id)
        if project:
            return jsonify(project)
        return jsonify({"error": "Project not found"}), 404
    
    @app.route("/api/projects")
    def get_projects():
        """Get all active projects"""
        return jsonify(manager.get_active_projects())
    
    @app.route("/api/projects/<project_id>/activity", methods=["POST"])
    def add_activity(project_id):
        """Add activity to a project"""
        data = request.get_json()
        success = manager.add_activity(
            project_id,
            agent=data.get("agent"),
            action=data.get("action"),
            details=data.get("details")
        )
        
        if success:
            # Emit activity update
            socketio.emit('activity_update', {
                'project_id': project_id,
                'agent': data.get("agent"),
                'action': data.get("action"),
                'details': data.get("details"),
                'timestamp': datetime.utcnow().isoformat() + "Z"
            })
            return jsonify({"status": "added"})
        
        return jsonify({"error": "Project not found"}), 404
    
    @app.route("/api/projects/<project_id>/complete", methods=["POST"])
    def complete_project(project_id):
        """Mark project as complete with output"""
        data = request.get_json()
        success = manager.set_project_output(
            project_id,
            output=data.get("output", "")
        )
        
        if success:
            # Emit completion event
            socketio.emit('project_complete', {
                'project_id': project_id,
                'output': data.get("output", "")
            })
            return jsonify({"status": "completed"})
        
        return jsonify({"error": "Project not found"}), 404
    
    @app.route("/api/projects/<project_id>/agents/<agent_name>/summary")
    def get_agent_summary(project_id, agent_name):
        """Get summary of agent's work on a project"""
        summary = manager.get_agent_summary(project_id, agent_name)
        return jsonify(summary)
    
    return manager