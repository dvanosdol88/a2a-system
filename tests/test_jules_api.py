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
                ["python", "jules_api.py"],
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
    
    def test_add_task_endpoint(self):
        """Test /add_task endpoint creates tasks properly"""
        task_data = {"task": TEST_TASK}
        response = requests.post(
            f"{API_BASE_URL}/add_task",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert TEST_TASK in data["message"]
        assert "total_tasks" in data
        assert data["total_tasks"] >= 1
    
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