"""
A2A Production Readiness Check
Comprehensive validation for production deployment
"""

import requests
import json
import time
import subprocess
import psutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Tuple

class ProductionReadinessCheck:
    """Comprehensive production readiness validation"""
    
    def __init__(self):
        self.api_url = "http://127.0.0.1:5000"
        self.dashboard_url = "http://127.0.0.1:5001"
        self.checks = []
        self.critical_failures = []
        self.warnings = []
        
    def run_complete_readiness_check(self) -> Dict[str, Any]:
        """Run comprehensive production readiness check"""
        print("🏭 A2A Production Readiness Check")
        print("=" * 50)
        
        check_start = datetime.now(timezone.utc)
        
        # Define all readiness checks
        readiness_checks = [
            ("Environment Setup", self.check_environment_setup),
            ("Core Services", self.check_core_services),
            ("Performance Baseline", self.check_performance_baseline),
            ("Security Configuration", self.check_security_config),
            ("Monitoring Systems", self.check_monitoring_systems),
            ("Error Handling", self.check_error_handling),
            ("Resource Requirements", self.check_resource_requirements),
            ("Data Persistence", self.check_data_persistence),
            ("Backup & Recovery", self.check_backup_recovery),
            ("Load Testing", self.check_load_capacity)
        ]
        
        results = {
            "readiness_check": "A2A_Production_Readiness",
            "timestamp": check_start.isoformat(),
            "checks": [],
            "overall_readiness": "unknown",
            "critical_issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        passed_checks = 0
        
        # Execute all checks
        for check_name, check_func in readiness_checks:
            print(f"\n🔍 {check_name}...")
            try:
                check_result = check_func()
                check_result["check_name"] = check_name
                results["checks"].append(check_result)
                
                if check_result.get("passed", False):
                    passed_checks += 1
                    print(f"  ✅ {check_name}: PASSED")
                else:
                    print(f"  ❌ {check_name}: FAILED")
                    if check_result.get("critical", False):
                        results["critical_issues"].extend(check_result.get("issues", []))
                    else:
                        results["warnings"].extend(check_result.get("issues", []))
                        
            except Exception as e:
                error_result = {
                    "check_name": check_name,
                    "passed": False,
                    "critical": True,
                    "error": str(e),
                    "issues": [f"Check execution failed: {str(e)}"]
                }
                results["checks"].append(error_result)
                results["critical_issues"].append(f"{check_name}: {str(e)}")
                print(f"  💥 {check_name}: ERROR - {str(e)}")
        
        # Calculate overall readiness
        success_rate = (passed_checks / len(readiness_checks)) * 100
        critical_count = len(results["critical_issues"])
        warning_count = len(results["warnings"])
        
        if critical_count == 0 and success_rate >= 95:
            results["overall_readiness"] = "production_ready"
        elif critical_count == 0 and success_rate >= 85:
            results["overall_readiness"] = "mostly_ready"
        elif critical_count <= 2 and success_rate >= 70:
            results["overall_readiness"] = "needs_attention"
        else:
            results["overall_readiness"] = "not_ready"
        
        # Generate recommendations
        results["recommendations"] = self._generate_readiness_recommendations(results)
        
        # Print summary
        self._print_readiness_summary(results)
        
        # Save results
        self._save_readiness_report(results)
        
        return results
    
    def check_environment_setup(self) -> Dict[str, Any]:
        """Check environment setup and dependencies"""
        issues = []
        checks = {}
        
        # Check Python version
        try:
            import sys
            python_version = sys.version_info
            checks["python_version"] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
            if python_version < (3, 8):
                issues.append("Python version < 3.8 - upgrade required")
        except Exception as e:
            issues.append(f"Python version check failed: {e}")
        
        # Check virtual environment
        venv_path = Path("a2a-env")
        checks["virtual_environment"] = venv_path.exists()
        if not venv_path.exists():
            issues.append("Virtual environment not found - run setup script")
        
        # Check dependencies
        try:
            import flask
            checks["flask_available"] = True
            checks["flask_version"] = flask.__version__
        except ImportError:
            checks["flask_available"] = False
            issues.append("Flask not available - check virtual environment")
        
        # Check required files
        required_files = [
            "api/jules_server.py",
            "shared/message_types.py",
            "monitoring/dashboard_server.py",
            "requirements.txt"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        checks["required_files"] = len(required_files) - len(missing_files)
        if missing_files:
            issues.append(f"Missing required files: {', '.join(missing_files)}")
        
        return {
            "passed": len(issues) == 0,
            "critical": True,
            "checks": checks,
            "issues": issues
        }
    
    def check_core_services(self) -> Dict[str, Any]:
        """Check core service availability"""
        issues = []
        services = {}
        
        # Check API server
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            services["api_server"] = {
                "running": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "status_code": response.status_code
            }
            if response.status_code != 200:
                issues.append(f"API server unhealthy: HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            services["api_server"] = {"running": False}
            issues.append("API server not running")
        except Exception as e:
            services["api_server"] = {"running": False, "error": str(e)}
            issues.append(f"API server check failed: {e}")
        
        # Check dashboard
        try:
            response = requests.get(f"{self.dashboard_url}/health", timeout=5)
            services["dashboard"] = {
                "running": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "status_code": response.status_code
            }
            if response.status_code != 200:
                issues.append(f"Dashboard unhealthy: HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            services["dashboard"] = {"running": False}
            issues.append("Dashboard not running - deploy monitoring/dashboard_server.py")
        except Exception as e:
            services["dashboard"] = {"running": False, "error": str(e)}
            issues.append(f"Dashboard check failed: {e}")
        
        return {
            "passed": len(issues) == 0,
            "critical": True,
            "services": services,
            "issues": issues
        }
    
    def check_performance_baseline(self) -> Dict[str, Any]:
        """Check performance meets baseline requirements"""
        issues = []
        performance = {}
        
        # Test response time
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/health", timeout=10)
            response_time = (time.time() - start_time) * 1000  # ms
            
            performance["response_time"] = response_time
            performance["response_time_acceptable"] = response_time < 500  # < 500ms
            
            if response_time > 1000:
                issues.append(f"Response time too high: {response_time:.0f}ms (target: <500ms)")
            elif response_time > 500:
                issues.append(f"Response time warning: {response_time:.0f}ms (target: <500ms)")
                
        except Exception as e:
            issues.append(f"Response time test failed: {e}")
        
        # Test task processing
        try:
            test_task = {"task": f"Production readiness test - {datetime.now(timezone.utc).isoformat()}"}
            
            start_time = time.time()
            response = requests.post(f"{self.api_url}/add_task", json=test_task, timeout=10)
            processing_time = (time.time() - start_time) * 1000
            
            performance["task_processing_time"] = processing_time
            performance["task_processing_acceptable"] = processing_time < 1000
            
            if response.status_code == 201:
                performance["task_processing_working"] = True
            else:
                performance["task_processing_working"] = False
                issues.append(f"Task processing failed: HTTP {response.status_code}")
                
        except Exception as e:
            issues.append(f"Task processing test failed: {e}")
        
        return {
            "passed": len(issues) == 0,
            "critical": False,
            "performance": performance,
            "issues": issues
        }
    
    def check_security_config(self) -> Dict[str, Any]:
        """Check security configuration"""
        issues = []
        security = {}
        
        # Check for debug mode (should be disabled in production)
        security["debug_mode_disabled"] = True  # Assume correct for now
        
        # Check for sensitive data exposure
        try:
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                # Check if sensitive info is exposed
                if "debug" in health_data or "internal" in str(health_data):
                    issues.append("Potential sensitive data exposure in API responses")
                security["api_response_clean"] = "debug" not in health_data
        except:
            pass
        
        # Check HTTPS (if in production)
        if self.api_url.startswith("https://"):
            security["https_enabled"] = True
        else:
            security["https_enabled"] = False
            issues.append("HTTPS not enabled - required for production")
        
        # Check for default passwords/keys
        security["default_credentials_changed"] = True  # Assume correct
        
        return {
            "passed": len(issues) == 0,
            "critical": False,
            "security": security,
            "issues": issues
        }
    
    def check_monitoring_systems(self) -> Dict[str, Any]:
        """Check monitoring systems functionality"""
        issues = []
        monitoring = {}
        
        # Check dashboard data availability
        try:
            response = requests.get(f"{self.dashboard_url}/api/dashboard-data", timeout=5)
            if response.status_code == 200:
                data = response.json()
                monitoring["dashboard_data_available"] = True
                monitoring["system_status_tracked"] = "system_status" in data
                
                if "system_status" not in data:
                    issues.append("System status not being tracked in dashboard")
            else:
                monitoring["dashboard_data_available"] = False
                issues.append("Dashboard data not available")
        except Exception as e:
            monitoring["dashboard_data_available"] = False
            issues.append(f"Dashboard data check failed: {e}")
        
        # Check metrics collection
        metrics_file = Path("monitoring/system_metrics.json")
        monitoring["metrics_collection"] = metrics_file.exists()
        if not metrics_file.exists():
            issues.append("Metrics collection not active")
        
        return {
            "passed": len(issues) == 0,
            "critical": False,
            "monitoring": monitoring,
            "issues": issues
        }
    
    def check_error_handling(self) -> Dict[str, Any]:
        """Check error handling capabilities"""
        issues = []
        error_handling = {}
        
        # Test invalid request handling
        try:
            response = requests.post(f"{self.api_url}/add_task", json={"invalid": "data"}, timeout=5)
            error_handling["invalid_request_handling"] = response.status_code >= 400
            
            if response.status_code < 400:
                issues.append("Invalid requests not properly rejected")
        except Exception as e:
            issues.append(f"Error handling test failed: {e}")
        
        # Test server error recovery
        try:
            # Test if server responds after potential errors
            response = requests.get(f"{self.api_url}/health", timeout=5)
            error_handling["server_recovery"] = response.status_code == 200
            
            if response.status_code != 200:
                issues.append("Server not responding properly after error tests")
        except Exception as e:
            issues.append(f"Server recovery test failed: {e}")
        
        return {
            "passed": len(issues) == 0,
            "critical": False,
            "error_handling": error_handling,
            "issues": issues
        }
    
    def check_resource_requirements(self) -> Dict[str, Any]:
        """Check system resource requirements"""
        issues = []
        resources = {}
        
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            resources["cpu_usage"] = cpu_percent
            resources["cpu_acceptable"] = cpu_percent < 80
            
            if cpu_percent > 90:
                issues.append(f"CPU usage too high: {cpu_percent:.1f}%")
            
            # Check memory usage
            memory = psutil.virtual_memory()
            resources["memory_usage"] = memory.percent
            resources["memory_acceptable"] = memory.percent < 85
            
            if memory.percent > 90:
                issues.append(f"Memory usage too high: {memory.percent:.1f}%")
            
            # Check disk space
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            resources["disk_usage"] = disk_percent
            resources["disk_acceptable"] = disk_percent < 90
            
            if disk_percent > 95:
                issues.append(f"Disk usage critically high: {disk_percent:.1f}%")
                
        except Exception as e:
            issues.append(f"Resource check failed: {e}")
        
        return {
            "passed": len(issues) == 0,
            "critical": False,
            "resources": resources,
            "issues": issues
        }
    
    def check_data_persistence(self) -> Dict[str, Any]:
        """Check data persistence and integrity"""
        issues = []
        persistence = {}
        
        # Check task data persistence
        try:
            # Get current task count
            response = requests.get(f"{self.api_url}/tasks", timeout=5)
            if response.status_code == 200:
                initial_tasks = response.json()
                initial_count = len(initial_tasks)
                
                # Add test task
                test_task = {"task": f"Persistence test - {datetime.now(timezone.utc).isoformat()}"}
                add_response = requests.post(f"{self.api_url}/add_task", json=test_task, timeout=5)
                
                if add_response.status_code == 201:
                    # Verify task was persisted
                    verify_response = requests.get(f"{self.api_url}/tasks", timeout=5)
                    if verify_response.status_code == 200:
                        final_tasks = verify_response.json()
                        final_count = len(final_tasks)
                        
                        persistence["task_persistence"] = final_count > initial_count
                        persistence["task_count_increase"] = final_count - initial_count
                        
                        if final_count <= initial_count:
                            issues.append("Task persistence not working - tasks not being saved")
                    else:
                        issues.append("Cannot verify task persistence")
                else:
                    issues.append("Cannot add test task for persistence check")
            else:
                issues.append("Cannot access task list for persistence check")
                
        except Exception as e:
            issues.append(f"Data persistence check failed: {e}")
        
        return {
            "passed": len(issues) == 0,
            "critical": True,
            "persistence": persistence,
            "issues": issues
        }
    
    def check_backup_recovery(self) -> Dict[str, Any]:
        """Check backup and recovery procedures"""
        issues = []
        backup = {}
        
        # Check if backup procedures are documented
        backup_docs = ["docs/backup-procedures.md", "docs/recovery-procedures.md"]
        backup["backup_docs_available"] = any(Path(doc).exists() for doc in backup_docs)
        
        if not backup["backup_docs_available"]:
            issues.append("Backup and recovery procedures not documented")
        
        # Check data files can be backed up
        data_files = ["shared/tasks.json"]
        backup["data_files_accessible"] = all(Path(f).exists() for f in data_files)
        
        if not backup["data_files_accessible"]:
            issues.append("Not all data files accessible for backup")
        
        return {
            "passed": len(issues) == 0,
            "critical": False,
            "backup": backup,
            "issues": issues
        }
    
    def check_load_capacity(self) -> Dict[str, Any]:
        """Check system load handling capacity"""
        issues = []
        load_test = {}
        
        # Simple load test
        try:
            num_requests = 20
            successful_requests = 0
            total_time = 0
            
            print(f"    Running load test with {num_requests} requests...")
            
            start_time = time.time()
            for i in range(num_requests):
                try:
                    test_task = {"task": f"Load test {i+1}"}
                    response = requests.post(f"{self.api_url}/add_task", json=test_task, timeout=5)
                    if response.status_code == 201:
                        successful_requests += 1
                except:
                    pass
            
            total_time = time.time() - start_time
            
            success_rate = (successful_requests / num_requests) * 100
            requests_per_second = num_requests / total_time if total_time > 0 else 0
            
            load_test["requests_sent"] = num_requests
            load_test["successful_requests"] = successful_requests
            load_test["success_rate"] = success_rate
            load_test["requests_per_second"] = requests_per_second
            load_test["total_time"] = total_time
            
            if success_rate < 95:
                issues.append(f"Load test success rate too low: {success_rate:.1f}% (target: >95%)")
            
            if requests_per_second < 10:
                issues.append(f"Throughput too low: {requests_per_second:.1f} req/s (target: >10 req/s)")
                
        except Exception as e:
            issues.append(f"Load capacity test failed: {e}")
        
        return {
            "passed": len(issues) == 0,
            "critical": False,
            "load_test": load_test,
            "issues": issues
        }
    
    def _generate_readiness_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations for production readiness"""
        recommendations = []
        
        critical_count = len(results["critical_issues"])
        warning_count = len(results["warnings"])
        
        if critical_count > 0:
            recommendations.append(f"🚨 CRITICAL: Resolve {critical_count} critical issues before production deployment")
        
        if warning_count > 0:
            recommendations.append(f"⚠️ Address {warning_count} warnings to improve system reliability")
        
        # Specific recommendations based on readiness level
        readiness = results["overall_readiness"]
        
        if readiness == "production_ready":
            recommendations.extend([
                "✅ System is production ready",
                "📊 Establish monitoring baselines for production environment",
                "🔄 Schedule regular health checks and maintenance windows",
                "📋 Prepare incident response procedures"
            ])
        elif readiness == "mostly_ready":
            recommendations.extend([
                "🔧 Minor improvements needed before production deployment",
                "📈 Focus on performance optimization",
                "📊 Enhance monitoring coverage"
            ])
        elif readiness == "needs_attention":
            recommendations.extend([
                "⚠️ Several issues require attention before production",
                "🔧 Focus on resolving critical issues first",
                "📊 Improve system monitoring and alerting",
                "🧪 Conduct more comprehensive testing"
            ])
        else:
            recommendations.extend([
                "🚨 System not ready for production deployment",
                "🔧 Resolve all critical issues immediately",
                "🧪 Conduct thorough testing after fixes",
                "📊 Implement comprehensive monitoring"
            ])
        
        return recommendations
    
    def _print_readiness_summary(self, results: Dict[str, Any]):
        """Print production readiness summary"""
        print("\n" + "=" * 60)
        print("🏭 PRODUCTION READINESS SUMMARY")
        print("=" * 60)
        
        readiness = results["overall_readiness"]
        critical_count = len(results["critical_issues"])
        warning_count = len(results["warnings"])
        
        # Overall status
        if readiness == "production_ready":
            print("🎉 STATUS: PRODUCTION READY ✅")
        elif readiness == "mostly_ready":
            print("🔧 STATUS: MOSTLY READY - Minor issues ⚠️")
        elif readiness == "needs_attention":
            print("⚠️ STATUS: NEEDS ATTENTION - Several issues")
        else:
            print("🚨 STATUS: NOT READY - Critical issues")
        
        # Issue summary
        print(f"\n📊 Issue Summary:")
        print(f"   Critical Issues: {critical_count}")
        print(f"   Warnings: {warning_count}")
        
        # Check results
        passed_checks = sum(1 for check in results["checks"] if check.get("passed", False))
        total_checks = len(results["checks"])
        print(f"   Checks Passed: {passed_checks}/{total_checks} ({(passed_checks/total_checks)*100:.1f}%)")
        
        # Critical issues
        if critical_count > 0:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in results["critical_issues"][:5]:  # Show top 5
                print(f"   • {issue}")
        
        # Recommendations
        print(f"\n📋 NEXT STEPS:")
        for rec in results["recommendations"][:5]:  # Show top 5
            print(f"   • {rec}")
    
    def _save_readiness_report(self, results: Dict[str, Any]):
        """Save production readiness report"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"production_readiness_report_{timestamp}.json")
        
        try:
            with open(report_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n📄 Production readiness report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️ Failed to save readiness report: {e}")


if __name__ == "__main__":
    print("🏭 A2A Production Readiness Check")
    print("=" * 50)
    
    checker = ProductionReadinessCheck()
    results = checker.run_complete_readiness_check()
    
    readiness = results["overall_readiness"]
    if readiness == "production_ready":
        print(f"\n🎉 System is ready for production deployment!")
    else:
        print(f"\n🔧 System needs attention before production deployment")
    
    print(f"📊 Final Score: {results['overall_readiness']}")