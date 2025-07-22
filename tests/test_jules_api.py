#!/usr/bin/env python3
"""
Test suite for Jules API Flask server
Created: 2025-07-04
Purpose: Verify Claude-Jules communication endpoints
"""

import pytest
import requests
import json
from pathlib import Path
import subprocess
import time
import os
import signal

# Test configuration
API_BASE_URL = "http://127.0.0.1:5000"
TEST_TASK = "Test task for validation"

class TestJulesAPI:
    """Test suite for Jules API endpoints"""
    
    @classmethod
    def setup_class(cls):
        """Start Jules API server for testing"""
        cls.server_process = None
        try:
            # Start server in background
            cls.server_process = subprocess.Popen(
                ["python", "-m", "api.jules_server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent.parent
            )
            # Wait for server to start
            time.sleep(2)
            
            # Verify server is running
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            assert response.status_code == 200
            
        except Exception as e:
            if cls.server_process:
                cls.server_process.terminate()
            pytest.skip(f"Could not start Jules API server: {e}")
    
    @classmethod
    def teardown_class(cls):
        """Stop Jules API server after testing"""
        if cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait(timeout=5)
    
    def test_health_endpoint(self):
        """Test /health endpoint returns proper status"""
        response = requests.get(f"{API_BASE_URL}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "server_time" in data
        assert data["server_time"].endswith("Z")
    
    def test_post_tasks(self):
        """Test POST /tasks endpoint."""
        response = requests.post(f"{API_BASE_URL}/tasks", json={"task": "test_task"})
        assert response.status_code == 201
        assert "task_id" in response.json()

    def test_put_task(self):
        """Test PUT /tasks/<id> endpoint."""
        response = requests.post(f"{API_BASE_URL}/tasks", json={"task": "test_task"})
        task_id = response.json()["task_id"]

        response = requests.put(f"{API_BASE_URL}/tasks/{task_id}", json={"status": "assigned"})
        assert response.status_code == 200

        # Verify the update
        response = requests.get(f"{API_BASE_URL}/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "assigned"

    def test_post_task_complete(self):
        """Test POST /tasks/<id>/complete endpoint."""
        response = requests.post(f"{API_BASE_URL}/tasks", json={"task": "test_task"})
        task_id = response.json()["task_id"]

        response = requests.post(f"{API_BASE_URL}/tasks/{task_id}/complete", json={"result": "some_result"})
        assert response.status_code == 200

    def test_get_unassigned_tasks(self):
        """Test GET /tasks/unassigned endpoint."""
        # Create a task without an assignment
        requests.post(f"{API_BASE_URL}/tasks", json={"task": "unassigned_task"})

        response = requests.get(f"{API_BASE_URL}/tasks/unassigned")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_add_task_validation(self):
        """Test /add_task endpoint validates required fields"""
        # Test empty task
        response = requests.post(
            f"{API_BASE_URL}/add_task",
            json={"task": ""},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "required" in data["error"]
        
        # Test missing task field
        response = requests.post(
            f"{API_BASE_URL}/add_task",
            json={},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
    
    def test_list_tasks_endpoint(self):
        """Test /tasks endpoint returns task list"""
        response = requests.get(f"{API_BASE_URL}/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Verify task structure if tasks exist
        if data:
            task = data[0]
            assert "task" in task
            assert "created" in task
            assert task["created"].endswith("Z")
    
    def test_task_persistence(self):
        """Test that tasks are persisted to shared/tasks.json"""
        # Add a unique task
        unique_task = f"Persistence test {time.time()}"
        requests.post(
            f"{API_BASE_URL}/add_task",
            json={"task": unique_task}
        )
        
        # Verify task appears in list
        response = requests.get(f"{API_BASE_URL}/tasks")
        tasks = response.json()
        
        task_found = any(task["task"] == unique_task for task in tasks)
        assert task_found, f"Task '{unique_task}' not found in task list"
        
        # Verify task is in file
        tasks_file = Path(__file__).parent.parent / "shared" / "tasks.json"
        if tasks_file.exists():
            file_tasks = json.loads(tasks_file.read_text())
            file_task_found = any(task["task"] == unique_task for task in file_tasks)
            assert file_task_found, f"Task '{unique_task}' not found in tasks.json"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])