#!/usr/bin/env python3
"""
A2A Hello World Message Test
Test basic agent-to-agent communication
"""

import requests
import json
import time
from datetime import datetime, timezone

def test_jules_server():
    """Test Jules server and send Hello World messages"""
    
    print("🧪 A2A HELLO WORLD MESSAGE TEST")
    print("=" * 40)
    
    jules_url = "http://127.0.0.1:5006"
    
    # Test 1: Health check
    print("\n🔍 Testing Jules Server Health...")
    try:
        response = requests.get(f"{jules_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Jules server healthy: {health_data}")
        else:
            print(f"❌ Jules server unhealthy: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Jules server - is it running on port 5006?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Send Hello World message from Claude to Jules
    print("\n📤 Claude → Jules: Hello World Message")
    hello_message = {
        "task": "Hello World from Claude! 👋 Testing A2A communication system."
    }
    
    try:
        response = requests.post(f"{jules_url}/add_task", json=hello_message, timeout=5)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Message sent successfully: {result}")
        else:
            print(f"❌ Failed to send message: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Message send error: {e}")
        return False
    
    # Test 3: Send more test messages
    test_messages = [
        "Hello from Claude - Testing basic communication",
        "A2A System Test Message #2 🚀",
        "Jules, can you receive this message? - Claude",
        "Final test message for Hello World demo 🎉"
    ]
    
    print("\n📤 Sending multiple test messages...")
    for i, msg in enumerate(test_messages, 1):
        try:
            response = requests.post(f"{jules_url}/add_task", 
                                   json={"task": f"Test {i}: {msg}"}, 
                                   timeout=5)
            if response.status_code == 201:
                print(f"✅ Message {i} sent successfully")
            else:
                print(f"❌ Message {i} failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Message {i} error: {e}")
    
    # Test 4: Retrieve all messages
    print("\n📥 Retrieving all messages from Jules...")
    try:
        response = requests.get(f"{jules_url}/tasks", timeout=5)
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ Retrieved {len(tasks)} messages:")
            
            for i, task in enumerate(tasks[-5:], 1):  # Show last 5 messages
                print(f"  {i}. {task.get('task', 'No task')}")
                print(f"     Created: {task.get('created', 'No timestamp')}")
                
        else:
            print(f"❌ Failed to retrieve messages: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Message retrieval error: {e}")
        return False
    
    # Test 5: Send a message "from CODEX"
    print("\n📤 Simulated CODEX → Jules Message")
    codex_message = {
        "task": "Hello Jules from CODEX! 🤖 Ready to coordinate tasks together."
    }
    
    try:
        response = requests.post(f"{jules_url}/add_task", json=codex_message, timeout=5)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ CODEX message sent: {result}")
        else:
            print(f"❌ CODEX message failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ CODEX message error: {e}")
    
    print("\n🎉 HELLO WORLD TEST COMPLETE!")
    print("✅ A2A Communication System Working!")
    print(f"🌐 Jules Server: {jules_url}")
    print("📋 Jules can receive and store messages from other agents")
    
    return True

if __name__ == "__main__":
    success = test_jules_server()
    if success:
        print("\n🎯 A2A Hello World Test: SUCCESS! 🎉")
    else:
        print("\n❌ A2A Hello World Test: FAILED")
        exit(1)