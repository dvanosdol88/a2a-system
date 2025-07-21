#!/usr/bin/env python3
"""
P3.2 Chaos Test - Simulate Redis Outage
"""
import requests
import time
import subprocess
import os

def run_chaos_test():
    """Run chaos test sequence"""
    print("=" * 60)
    print("P3.2 CHAOS TEST - REDIS OUTAGE SIMULATION")
    print("=" * 60)
    
    results = []
    base_url = "http://localhost:5001"
    
    # Test 1: Normal operation (using existing server on 5001)
    print("\n1. Testing with Redis connected...")
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        status1 = resp.status_code
        data1 = resp.json()
        print(f"   Status: {status1} - Redis: {data1.get('redis')} - Storage: {data1.get('storage')}")
        results.append(("Normal Operation", status1))
    except Exception as e:
        print(f"   Error: {e}")
        results.append(("Normal Operation", "ERROR"))
    
    # Test 2: Start server with Redis unavailable
    print("\n2. Starting server with Redis unavailable...")
    env = os.environ.copy()
    env['REDIS_HOST'] = 'nonexistent.redis.host'
    env['A2A_JULES_PORT'] = '5004'
    
    # Kill any existing process on 5004
    subprocess.run(['pkill', '-f', 'A2A_JULES_PORT=5004'], capture_output=True)
    time.sleep(1)
    
    # Start server with bad Redis host
    proc = subprocess.Popen(
        ['venv/bin/python', '-m', 'api.jules_server'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)  # Wait for server to start
    
    try:
        resp = requests.get("http://localhost:5004/health", timeout=5)
        status2 = resp.status_code
        data2 = resp.json()
        print(f"   Status: {status2} - Redis: {data2.get('redis')} - Storage: {data2.get('storage')}")
        results.append(("Redis Outage", status2))
    except Exception as e:
        print(f"   Error: {e}")
        results.append(("Redis Outage", "ERROR"))
    
    # Kill the test server
    proc.terminate()
    proc.wait()
    
    # Test 3: Server with Redis restored (back to 5001)
    print("\n3. Testing after Redis restoration...")
    time.sleep(2)
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        status3 = resp.status_code
        data3 = resp.json()
        print(f"   Status: {status3} - Redis: {data3.get('redis')} - Storage: {data3.get('storage')}")
        results.append(("Redis Restored", status3))
    except Exception as e:
        print(f"   Error: {e}")
        results.append(("Redis Restored", "ERROR"))
    
    # Summary
    print("\n" + "=" * 60)
    print("CHAOS TEST SUMMARY - HTTP Status Codes")
    print("=" * 60)
    
    for test_name, status in results:
        print(f"{test_name}: {status}")
    
    print("\nExpected sequence: 200 -> 200 (with fallback) -> 200")
    print("Actual sequence: {} -> {} -> {}".format(
        results[0][1], results[1][1], results[2][1]
    ))
    
    return results

if __name__ == "__main__":
    run_chaos_test()