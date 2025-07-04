"""
Jules Status Check - Simplified A2A System Diagnostic
Quick health check without external dependencies
"""

import requests
import json
from datetime import datetime, timezone
import time

def check_jules_status():
    """Check Jules and A2A system status"""
    print("🔍 Checking Jules Status...")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "api_server": {},
        "task_queue": {},
        "monitoring_dashboard": {},
        "diagnosis": []
    }
    
    # Check API Server
    print("📡 Checking Jules API Server (Port 5000)...")
    try:
        start_time = time.time()
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            health_data = response.json()
            results["api_server"] = {
                "status": "✅ RUNNING",
                "response_time": f"{response_time:.0f}ms",
                "server_time": health_data.get("server_time"),
                "details": health_data
            }
            print(f"  ✅ API Server: HEALTHY ({response_time:.0f}ms)")
        else:
            results["api_server"] = {
                "status": "❌ ERROR",
                "http_code": response.status_code,
                "response_time": f"{response_time:.0f}ms"
            }
            print(f"  ❌ API Server: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        results["api_server"] = {
            "status": "❌ NOT RUNNING",
            "error": "Connection refused"
        }
        print("  ❌ API Server: NOT RUNNING")
        results["diagnosis"].append("Jules API server is not running - needs to start api/jules_server.py")
        
    except Exception as e:
        results["api_server"] = {
            "status": "❌ ERROR",
            "error": str(e)
        }
        print(f"  ❌ API Server: ERROR - {e}")
    
    # Check Task Queue
    print("\n📋 Checking Task Queue...")
    try:
        response = requests.get("http://127.0.0.1:5000/tasks", timeout=5)
        if response.status_code == 200:
            tasks = response.json()
            results["task_queue"] = {
                "status": "✅ ACCESSIBLE",
                "task_count": len(tasks),
                "recent_tasks": tasks[-3:] if tasks else []
            }
            print(f"  ✅ Task Queue: {len(tasks)} tasks")
            
            if tasks:
                print("  📝 Recent tasks:")
                for task in tasks[-3:]:
                    created = task.get("created", "unknown")
                    description = task.get("task", "")[:50] + "..." if len(task.get("task", "")) > 50 else task.get("task", "")
                    print(f"    - {created}: {description}")
            else:
                print("  📝 No tasks in queue")
        else:
            results["task_queue"] = {
                "status": "❌ ERROR",
                "http_code": response.status_code
            }
            print(f"  ❌ Task Queue: HTTP {response.status_code}")
            
    except Exception as e:
        results["task_queue"] = {
            "status": "❌ ERROR",
            "error": str(e)
        }
        print(f"  ❌ Task Queue: ERROR - {e}")
    
    # Check Monitoring Dashboard
    print("\n📊 Checking Monitoring Dashboard (Port 5001)...")
    try:
        response = requests.get("http://127.0.0.1:5001/health", timeout=5)
        if response.status_code == 200:
            dashboard_data = response.json()
            results["monitoring_dashboard"] = {
                "status": "✅ RUNNING",
                "service": dashboard_data.get("service"),
                "monitoring_active": dashboard_data.get("monitoring_active")
            }
            print(f"  ✅ Dashboard: RUNNING (monitoring: {dashboard_data.get('monitoring_active')})")
        else:
            results["monitoring_dashboard"] = {
                "status": "❌ ERROR",
                "http_code": response.status_code
            }
            print(f"  ❌ Dashboard: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        results["monitoring_dashboard"] = {
            "status": "❌ NOT RUNNING",
            "error": "Connection refused"
        }
        print("  ❌ Dashboard: NOT RUNNING")
        results["diagnosis"].append("Monitoring dashboard not running - Jules should start monitoring/dashboard_server.py")
        
    except Exception as e:
        results["monitoring_dashboard"] = {
            "status": "❌ ERROR",
            "error": str(e)
        }
        print(f"  ❌ Dashboard: ERROR - {e}")
    
    # Test Task Creation
    print("\n🧪 Testing Task Creation...")
    try:
        test_task = {
            "task": f"Status check test - {datetime.now(timezone.utc).isoformat()}"
        }
        
        start_time = time.time()
        response = requests.post("http://127.0.0.1:5000/add_task", json=test_task, timeout=5)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 201:
            result_data = response.json()
            print(f"  ✅ Task Creation: SUCCESS ({response_time:.0f}ms)")
            print(f"    📝 {result_data.get('message')}")
        else:
            print(f"  ❌ Task Creation: HTTP {response.status_code}")
            results["diagnosis"].append("Task creation failing - API server may have issues")
            
    except Exception as e:
        print(f"  ❌ Task Creation: ERROR - {e}")
        results["diagnosis"].append("Cannot create tasks - API server connection issues")
    
    # Overall Diagnosis
    print("\n🔍 DIAGNOSIS:")
    print("=" * 50)
    
    api_running = "RUNNING" in results["api_server"].get("status", "")
    dashboard_running = "RUNNING" in results["monitoring_dashboard"].get("status", "")
    
    if api_running and dashboard_running:
        print("✅ Jules is FULLY OPERATIONAL")
        print("   Both API server and monitoring dashboard are running")
    elif api_running and not dashboard_running:
        print("⚠️ Jules is PARTIALLY OPERATIONAL")
        print("   API server running, but monitoring dashboard is down")
        print("   Jules should run: python monitoring/dashboard_server.py")
    elif not api_running and dashboard_running:
        print("⚠️ UNUSUAL STATE - Dashboard running but API server down")
        print("   This shouldn't happen - check system state")
    else:
        print("❌ Jules appears to be OFFLINE")
        print("   Neither API server nor dashboard are responding")
        print("   Jules needs to:")
        print("   1. cd /mnt/c/Users/david/projects-master/a2a-system")
        print("   2. source a2a-env/bin/activate")
        print("   3. python api/jules_server.py")
    
    if results["diagnosis"]:
        print("\n🔧 SPECIFIC ISSUES:")
        for issue in results["diagnosis"]:
            print(f"   • {issue}")
    
    # Jules Progress Assessment
    print("\n📈 JULES PROGRESS ASSESSMENT:")
    print("=" * 50)
    
    if api_running:
        print("✅ Phase 1: API Server - COMPLETE")
    else:
        print("❌ Phase 1: API Server - NEEDS ATTENTION")
    
    if dashboard_running:
        print("✅ Phase 3: Monitoring Dashboard - COMPLETE") 
    else:
        print("⏳ Phase 3: Monitoring Dashboard - IN PROGRESS")
    
    print("\n📋 NEXT STEPS FOR JULES:")
    if not api_running:
        print("1. URGENT: Start API server (api/jules_server.py)")
    if not dashboard_running:
        print("2. Deploy monitoring dashboard (monitoring/dashboard_server.py)")
    
    print("3. Run comprehensive testing (tests/enhanced_test_framework.py)")
    print("4. Begin operational monitoring procedures")
    
    # Save results
    with open("jules_status_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Full report saved to: jules_status_report.json")
    
    return results

if __name__ == "__main__":
    check_jules_status()