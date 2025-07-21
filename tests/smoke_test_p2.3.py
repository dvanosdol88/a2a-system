#!/usr/bin/env python3
"""
P2.3 End-to-End Smoke Test
Created: 2025-07-21
Purpose: Comprehensive smoke test for Jules API with Redis integration
"""

import sys
import time
from pathlib import Path
import json

# Import from the correct path
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))
from claude_to_jules_helper import JulesAPIClient

def run_smoke_tests():
    """Run comprehensive smoke tests for Jules API"""
    client = JulesAPIClient()
    results = []
    
    print("=" * 60)
    print("P2.3 END-TO-END SMOKE TEST")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing health endpoint...")
    health = client.health_check()
    if health.get("status") == "ok" and health.get("redis") == "connected":
        print("✅ Health check passed - Redis connected")
        results.append(("Health Check", "PASS"))
    else:
        print("❌ Health check failed")
        results.append(("Health Check", "FAIL"))
        return results
    
    # Test 2: Add Task without assignment
    print("\n2. Testing add_task without assignment...")
    task1 = client.add_task("Smoke test task 1")
    if "message" in task1 and "id" in task1:
        print(f"✅ Task added successfully: ID={task1['id']}")
        results.append(("Add Task (unassigned)", "PASS"))
    else:
        print("❌ Failed to add task")
        results.append(("Add Task (unassigned)", "FAIL"))
    
    # Test 3: Add Task with assignment
    print("\n3. Testing add_task with assignment...")
    task2_data = {"task": "Smoke test task 2", "assigned_to": "test_agent"}
    response = client.session.post(f"{client.base_url}/add_task", json=task2_data)
    task2 = response.json()
    if task2.get("assigned_to") == "test_agent":
        print(f"✅ Task assigned successfully: ID={task2['id']}, Agent={task2['assigned_to']}")
        results.append(("Add Task (assigned)", "PASS"))
    else:
        print("❌ Failed to assign task")
        results.append(("Add Task (assigned)", "FAIL"))
    
    # Test 4: List Tasks
    print("\n4. Testing list_tasks...")
    tasks = client.list_tasks()
    if isinstance(tasks, list) and len(tasks) > 0:
        print(f"✅ Listed {len(tasks)} tasks successfully")
        results.append(("List Tasks", "PASS"))
    else:
        print("❌ Failed to list tasks")
        results.append(("List Tasks", "FAIL"))
    
    # Test 5: Get Agent Tasks
    print("\n5. Testing agent-specific tasks...")
    agent_response = client.session.get(f"{client.base_url}/agent/test_agent/tasks")
    agent_tasks = agent_response.json()
    if isinstance(agent_tasks, list):
        print(f"✅ Retrieved {len(agent_tasks)} agent tasks")
        results.append(("Agent Tasks", "PASS"))
    else:
        print("❌ Failed to get agent tasks")
        results.append(("Agent Tasks", "FAIL"))
    
    # Test 6: Acknowledge Task
    if agent_tasks and len(agent_tasks) > 0:
        print("\n6. Testing task acknowledgment...")
        task_id = agent_tasks[0]["id"]
        ack_response = client.session.post(
            f"{client.base_url}/agent/test_agent/tasks/{task_id}/acknowledge"
        )
        if ack_response.status_code == 200:
            print(f"✅ Task {task_id} acknowledged successfully")
            results.append(("Acknowledge Task", "PASS"))
        else:
            print("❌ Failed to acknowledge task")
            results.append(("Acknowledge Task", "FAIL"))
    
    # Test 7: Complete Task
    if agent_tasks and len(agent_tasks) > 0:
        print("\n7. Testing task completion...")
        task_id = agent_tasks[0]["id"]
        complete_data = {"response": "Smoke test completed successfully"}
        complete_response = client.session.post(
            f"{client.base_url}/agent/test_agent/tasks/{task_id}/complete",
            json=complete_data
        )
        if complete_response.status_code == 200:
            print(f"✅ Task {task_id} completed successfully")
            results.append(("Complete Task", "PASS"))
        else:
            print("❌ Failed to complete task")
            results.append(("Complete Task", "FAIL"))
    
    # Summary
    print("\n" + "=" * 60)
    print("SMOKE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, status in results if status == "PASS")
    total = len(results)
    
    for test_name, status in results:
        symbol = "✅" if status == "PASS" else "❌"
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL SMOKE TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = run_smoke_tests()
    sys.exit(exit_code)