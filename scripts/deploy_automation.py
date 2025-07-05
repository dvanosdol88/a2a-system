"""
A2A Deployment Automation
Automated deployment and validation scripts
"""

import subprocess
import time
import requests
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

class A2ADeployment:
    """Automated A2A system deployment"""
    
    def __init__(self):
        self.deployment_log = []
        self.services = {}
        self.validation_results = {}
        
    def deploy_complete_system(self) -> Dict[str, Any]:
        """Deploy complete A2A system with validation"""
        print("🚀 A2A System Automated Deployment")
        print("=" * 50)
        
        deployment_start = datetime.now(timezone.utc)
        
        deployment_steps = [
            ("Environment Setup", self.deploy_environment),
            ("API Server", self.deploy_api_server),
            ("Monitoring Dashboard", self.deploy_dashboard),
            ("System Validation", self.validate_deployment),
            ("Performance Testing", self.run_performance_tests),
            ("Health Checks", self.setup_health_monitoring)
        ]
        
        deployment_results = {
            "deployment_id": f"a2a_deploy_{int(time.time())}",
            "start_time": deployment_start.isoformat(),
            "steps": [],
            "overall_success": False,
            "services_deployed": {},
            "validation_results": {}
        }
        
        try:
            for step_name, step_func in deployment_steps:
                print(f"\n🔧 {step_name}...")
                step_start = time.time()
                
                try:
                    step_result = step_func()
                    step_duration = time.time() - step_start
                    
                    step_result.update({
                        "step_name": step_name,
                        "duration": step_duration,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
                    deployment_results["steps"].append(step_result)
                    
                    if step_result.get("success", False):
                        print(f"  ✅ {step_name}: SUCCESS ({step_duration:.1f}s)")
                    else:
                        print(f"  ❌ {step_name}: FAILED ({step_duration:.1f}s)")
                        # Continue with other steps for partial deployment
                        
                except Exception as e:
                    error_result = {
                        "step_name": step_name,
                        "success": False,
                        "error": str(e),
                        "duration": time.time() - step_start,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    deployment_results["steps"].append(error_result)
                    print(f"  💥 {step_name}: ERROR - {str(e)}")
            
            # Calculate overall success
            successful_steps = sum(1 for step in deployment_results["steps"] if step.get("success", False))
            total_steps = len(deployment_steps)
            success_rate = (successful_steps / total_steps) * 100
            
            deployment_results["overall_success"] = success_rate >= 80  # 80% success threshold
            deployment_results["success_rate"] = success_rate
            deployment_results["successful_steps"] = successful_steps
            deployment_results["total_steps"] = total_steps
            
        except Exception as e:
            deployment_results["deployment_error"] = str(e)
            print(f"💥 Deployment failed with critical error: {e}")
        
        finally:
            deployment_end = datetime.now(timezone.utc)
            deployment_results["end_time"] = deployment_end.isoformat()
            deployment_results["total_duration"] = (deployment_end - deployment_start).total_seconds()
        
        # Print deployment summary
        self._print_deployment_summary(deployment_results)
        
        # Save deployment log
        self._save_deployment_log(deployment_results)
        
        return deployment_results
    
    def deploy_environment(self) -> Dict[str, Any]:
        """Deploy and validate environment setup"""
        try:
            # Check if virtual environment exists
            venv_path = Path("a2a-env")
            if not venv_path.exists():
                print("    📦 Creating virtual environment...")
                result = subprocess.run(["./scripts/setup-offline.sh"], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Environment setup failed: {result.stderr}",
                        "stdout": result.stdout
                    }
            
            # Verify environment
            print("    🔍 Verifying environment...")
            verify_result = subprocess.run([
                "bash", "-c", 
                "source a2a-env/bin/activate && python -c 'import flask; print(flask.__version__)'"
            ], capture_output=True, text=True, timeout=30)
            
            if verify_result.returncode == 0:
                flask_version = verify_result.stdout.strip()
                return {
                    "success": True,
                    "flask_version": flask_version,
                    "environment_ready": True
                }
            else:
                return {
                    "success": False,
                    "error": f"Environment verification failed: {verify_result.stderr}"
                }
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Environment setup timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def deploy_api_server(self) -> Dict[str, Any]:
        """Deploy Jules API server"""
        try:
            print("    🔄 Starting API server...")
            
            # Start API server in background
            api_process = subprocess.Popen([
                "bash", "-c",
                "source a2a-env/bin/activate && python api/jules_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(5)
            
            # Check if server is running
            try:
                response = requests.get("http://127.0.0.1:5000/health", timeout=10)
                if response.status_code == 200:
                    health_data = response.json()
                    self.services["api_server"] = {
                        "process": api_process,
                        "url": "http://127.0.0.1:5000",
                        "status": "running"
                    }
                    return {
                        "success": True,
                        "server_url": "http://127.0.0.1:5000",
                        "health_data": health_data,
                        "response_time": response.elapsed.total_seconds()
                    }
                else:
                    api_process.terminate()
                    return {
                        "success": False,
                        "error": f"API server unhealthy: HTTP {response.status_code}"
                    }
            except requests.exceptions.ConnectionError:
                api_process.terminate()
                return {
                    "success": False,
                    "error": "API server not responding after startup"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def deploy_dashboard(self) -> Dict[str, Any]:
        """Deploy monitoring dashboard"""
        try:
            print("    📊 Starting monitoring dashboard...")
            
            # Start dashboard in background
            dashboard_process = subprocess.Popen([
                "bash", "-c",
                "source a2a-env/bin/activate && python monitoring/dashboard_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for dashboard to start
            time.sleep(8)
            
            # Check if dashboard is running
            try:
                response = requests.get("http://127.0.0.1:5001/health", timeout=10)
                if response.status_code == 200:
                    dashboard_data = response.json()
                    self.services["dashboard"] = {
                        "process": dashboard_process,
                        "url": "http://127.0.0.1:5001",
                        "status": "running"
                    }
                    return {
                        "success": True,
                        "dashboard_url": "http://127.0.0.1:5001",
                        "dashboard_data": dashboard_data,
                        "response_time": response.elapsed.total_seconds()
                    }
                else:
                    dashboard_process.terminate()
                    return {
                        "success": False,
                        "error": f"Dashboard unhealthy: HTTP {response.status_code}"
                    }
            except requests.exceptions.ConnectionError:
                dashboard_process.terminate()
                return {
                    "success": False,
                    "error": "Dashboard not responding after startup"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def validate_deployment(self) -> Dict[str, Any]:
        """Validate deployed system"""
        validation_results = {}
        issues = []
        
        # Validate API functionality
        try:
            # Test health endpoint
            response = requests.get("http://127.0.0.1:5000/health", timeout=5)
            validation_results["api_health"] = response.status_code == 200
            
            # Test task creation
            test_task = {"task": f"Deployment validation - {datetime.now(timezone.utc).isoformat()}"}
            response = requests.post("http://127.0.0.1:5000/add_task", json=test_task, timeout=5)
            validation_results["task_creation"] = response.status_code == 201
            
            # Test task retrieval
            response = requests.get("http://127.0.0.1:5000/tasks", timeout=5)
            validation_results["task_retrieval"] = response.status_code == 200
            
            if not all([validation_results["api_health"], validation_results["task_creation"], validation_results["task_retrieval"]]):
                issues.append("API functionality validation failed")
                
        except Exception as e:
            issues.append(f"API validation error: {e}")
            validation_results["api_error"] = str(e)
        
        # Validate dashboard functionality
        try:
            response = requests.get("http://127.0.0.1:5001/api/dashboard-data", timeout=5)
            validation_results["dashboard_data"] = response.status_code == 200
            
            if response.status_code == 200:
                data = response.json()
                validation_results["dashboard_monitoring"] = "system_status" in data
            else:
                issues.append("Dashboard data not available")
                
        except Exception as e:
            issues.append(f"Dashboard validation error: {e}")
            validation_results["dashboard_error"] = str(e)
        
        # Validate data persistence
        try:
            tasks_file = Path("shared/tasks.json")
            validation_results["data_persistence"] = tasks_file.exists()
            
            if not tasks_file.exists():
                issues.append("Task data persistence not working")
                
        except Exception as e:
            issues.append(f"Data persistence validation error: {e}")
        
        success = len(issues) == 0
        
        return {
            "success": success,
            "validation_results": validation_results,
            "issues": issues
        }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run basic performance tests"""
        try:
            print("    🏃 Running performance tests...")
            
            # Response time test
            response_times = []
            for i in range(10):
                start_time = time.time()
                response = requests.get("http://127.0.0.1:5000/health", timeout=5)
                response_time = (time.time() - start_time) * 1000
                if response.status_code == 200:
                    response_times.append(response_time)
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
                
                performance_acceptable = avg_response_time < 500  # < 500ms
                
                return {
                    "success": performance_acceptable,
                    "avg_response_time": avg_response_time,
                    "max_response_time": max_response_time,
                    "min_response_time": min_response_time,
                    "test_count": len(response_times),
                    "performance_acceptable": performance_acceptable
                }
            else:
                return {
                    "success": False,
                    "error": "No successful performance test responses"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def setup_health_monitoring(self) -> Dict[str, Any]:
        """Setup ongoing health monitoring"""
        try:
            # Verify monitoring is working
            if "dashboard" in self.services:
                dashboard_url = self.services["dashboard"]["url"]
                
                # Start monitoring
                response = requests.post(f"{dashboard_url}/api/monitoring/start", timeout=5)
                monitoring_started = response.status_code == 200
                
                return {
                    "success": monitoring_started,
                    "monitoring_active": monitoring_started,
                    "dashboard_url": dashboard_url
                }
            else:
                return {
                    "success": False,
                    "error": "Dashboard not available for health monitoring setup"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def shutdown_services(self):
        """Shutdown deployed services"""
        print("🛑 Shutting down services...")
        
        for service_name, service_info in self.services.items():
            try:
                if "process" in service_info:
                    process = service_info["process"]
                    process.terminate()
                    process.wait(timeout=10)
                    print(f"  ✅ {service_name} shutdown complete")
            except Exception as e:
                print(f"  ⚠️ {service_name} shutdown error: {e}")
    
    def _print_deployment_summary(self, results: Dict[str, Any]):
        """Print deployment summary"""
        print("\n" + "=" * 60)
        print("🚀 DEPLOYMENT SUMMARY")
        print("=" * 60)
        
        success_rate = results.get("success_rate", 0)
        successful_steps = results.get("successful_steps", 0)
        total_steps = results.get("total_steps", 0)
        
        if results.get("overall_success", False):
            print("🎉 DEPLOYMENT: SUCCESS ✅")
        else:
            print("⚠️ DEPLOYMENT: PARTIAL SUCCESS ⚠️")
        
        print(f"\n📊 Results:")
        print(f"   Steps Completed: {successful_steps}/{total_steps} ({success_rate:.1f}%)")
        print(f"   Total Duration: {results.get('total_duration', 0):.1f} seconds")
        
        # Service status
        print(f"\n🔧 Services Deployed:")
        for service_name, service_info in self.services.items():
            status = service_info.get("status", "unknown")
            url = service_info.get("url", "N/A")
            print(f"   • {service_name}: {status} ({url})")
        
        # Failed steps
        failed_steps = [step for step in results["steps"] if not step.get("success", False)]
        if failed_steps:
            print(f"\n❌ Failed Steps:")
            for step in failed_steps[:3]:  # Show first 3 failures
                print(f"   • {step['step_name']}: {step.get('error', 'Unknown error')}")
    
    def _save_deployment_log(self, results: Dict[str, Any]):
        """Save deployment log"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_file = Path(f"deployment_log_{timestamp}.json")
        
        try:
            with open(log_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n📄 Deployment log saved to: {log_file}")
        except Exception as e:
            print(f"\n⚠️ Failed to save deployment log: {e}")


if __name__ == "__main__":
    print("🚀 A2A Automated Deployment")
    print("=" * 50)
    
    deployment = A2ADeployment()
    
    try:
        results = deployment.deploy_complete_system()
        
        if results.get("overall_success", False):
            print(f"\n🎉 Deployment successful! System is operational.")
            print(f"🌐 API Server: http://127.0.0.1:5000")
            print(f"📊 Dashboard: http://127.0.0.1:5001")
            
            input("\nPress Enter to shutdown services...")
        else:
            print(f"\n⚠️ Deployment completed with issues. Check logs for details.")
    
    except KeyboardInterrupt:
        print(f"\n⏹️ Deployment interrupted by user")
    
    finally:
        deployment.shutdown_services()
        print(f"✅ Deployment process complete")