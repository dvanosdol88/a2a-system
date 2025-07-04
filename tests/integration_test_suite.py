"""
A2A System Integration Test Suite
End-to-end testing for complete system validation
"""

import pytest
import requests
import json
import time
import threading
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import statistics

from shared.message_types import A2AMessage, MessageBuilder, MessageType
from tests.test_data_generator import TestDataGenerator
from monitoring.advanced_analytics import PerformanceAnalyzer, PerformanceBaseline
from monitoring.performance_optimizer import PerformanceOptimizer


class IntegrationTestSuite:
    """Comprehensive integration testing for A2A system"""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:5000", 
                 dashboard_url: str = "http://127.0.0.1:5001"):
        self.api_base_url = api_base_url
        self.dashboard_url = dashboard_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        self.test_results = {}
        self.performance_data = []
        self.error_log = []
        
        # Initialize components
        self.data_generator = TestDataGenerator(seed=42)
        self.analyzer = PerformanceAnalyzer()
        self.baseline = PerformanceBaseline()
        self.optimizer = PerformanceOptimizer()
        
    def run_full_integration_test(self) -> Dict[str, Any]:
        """Run complete integration test suite"""
        print("🧪 Starting A2A System Integration Test Suite")
        print("=" * 60)
        
        test_start_time = datetime.now(timezone.utc)
        
        # Test suite structure
        test_categories = [
            ("System Health Check", self.test_system_health),
            ("API Functionality", self.test_api_functionality),
            ("Message Type Processing", self.test_message_type_processing),
            ("Performance Under Load", self.test_performance_under_load),
            ("Error Handling & Recovery", self.test_error_handling),
            ("Monitoring Integration", self.test_monitoring_integration),
            ("Analytics & Optimization", self.test_analytics_optimization),
            ("End-to-End Workflows", self.test_end_to_end_workflows),
            ("Stress Testing", self.test_stress_scenarios),
            ("Data Persistence", self.test_data_persistence)
        ]
        
        suite_results = {
            "test_suite": "A2A_Integration_Test_Suite",
            "start_time": test_start_time.isoformat(),
            "test_categories": [],
            "overall_summary": {}
        }
        
        passed_categories = 0
        total_tests = 0
        passed_tests = 0
        
        # Execute test categories
        for category_name, test_method in test_categories:
            print(f"\n🔍 Testing: {category_name}")
            print("-" * 40)
            
            try:
                category_result = test_method()
                category_result["category_name"] = category_name
                category_result["execution_time"] = category_result.get("execution_time", 0)
                
                suite_results["test_categories"].append(category_result)
                
                category_passed = category_result.get("overall_passed", False)
                category_test_count = len(category_result.get("tests", []))
                category_passed_count = sum(1 for test in category_result.get("tests", []) if test.get("passed", False))
                
                if category_passed:
                    passed_categories += 1
                    print(f"✅ {category_name}: PASSED ({category_passed_count}/{category_test_count})")
                else:
                    print(f"❌ {category_name}: FAILED ({category_passed_count}/{category_test_count})")
                
                total_tests += category_test_count
                passed_tests += category_passed_count
                
            except Exception as e:
                error_result = {
                    "category_name": category_name,
                    "overall_passed": False,
                    "error": str(e),
                    "tests": []
                }
                suite_results["test_categories"].append(error_result)
                print(f"❌ {category_name}: ERROR - {str(e)}")
        
        # Calculate overall results
        test_end_time = datetime.now(timezone.utc)
        total_execution_time = (test_end_time - test_start_time).total_seconds()
        
        suite_results.update({
            "end_time": test_end_time.isoformat(),
            "total_execution_time": total_execution_time,
            "overall_summary": {
                "total_categories": len(test_categories),
                "passed_categories": passed_categories,
                "failed_categories": len(test_categories) - passed_categories,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
                "category_success_rate": (passed_categories / len(test_categories)) * 100
            }
        })
        
        # Print final summary
        self._print_test_summary(suite_results)
        
        # Save results
        self._save_test_results(suite_results)
        
        return suite_results
    
    def test_system_health(self) -> Dict[str, Any]:
        """Test overall system health and connectivity"""
        test_start = time.time()
        tests = []
        
        # Test API server health
        try:
            response = self.session.get(f"{self.api_base_url}/health", timeout=5)
            tests.append({
                "name": "api_server_health",
                "passed": response.status_code == 200,
                "details": {"status_code": response.status_code, "response": response.json() if response.status_code == 200 else response.text}
            })
        except Exception as e:
            tests.append({
                "name": "api_server_health",
                "passed": False,
                "error": str(e)
            })
        
        # Test dashboard connectivity
        try:
            response = requests.get(f"{self.dashboard_url}/health", timeout=5)
            tests.append({
                "name": "dashboard_connectivity",
                "passed": response.status_code == 200,
                "details": {"status_code": response.status_code, "response": response.json() if response.status_code == 200 else response.text}
            })
        except Exception as e:
            tests.append({
                "name": "dashboard_connectivity",
                "passed": False,
                "error": str(e)
            })
        
        # Test basic API endpoints
        endpoints = ["/tasks", "/health"]
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.api_base_url}{endpoint}", timeout=5)
                tests.append({
                    "name": f"endpoint_{endpoint.replace('/', '_')}",
                    "passed": response.status_code in [200, 201],
                    "details": {"endpoint": endpoint, "status_code": response.status_code}
                })
            except Exception as e:
                tests.append({
                    "name": f"endpoint_{endpoint.replace('/', '_')}",
                    "passed": False,
                    "error": str(e)
                })
        
        execution_time = time.time() - test_start
        passed_tests = sum(1 for test in tests if test["passed"])
        
        return {
            "overall_passed": passed_tests == len(tests),
            "tests": tests,
            "execution_time": execution_time,
            "summary": f"{passed_tests}/{len(tests)} health checks passed"
        }
    
    def test_api_functionality(self) -> Dict[str, Any]:
        """Test core API functionality"""
        test_start = time.time()
        tests = []
        
        # Test task creation
        test_task = {"task": f"Integration test task - {datetime.now(timezone.utc).isoformat()}"}
        try:
            response = self.session.post(f"{self.api_base_url}/add_task", json=test_task)
            tests.append({
                "name": "task_creation",
                "passed": response.status_code == 201,
                "details": {"status_code": response.status_code, "response": response.json() if response.status_code == 201 else response.text}
            })
        except Exception as e:
            tests.append({
                "name": "task_creation",
                "passed": False,
                "error": str(e)
            })
        
        # Test task retrieval
        try:
            response = self.session.get(f"{self.api_base_url}/tasks")
            task_list = response.json() if response.status_code == 200 else []
            tests.append({
                "name": "task_retrieval",
                "passed": response.status_code == 200,
                "details": {"status_code": response.status_code, "task_count": len(task_list)}
            })
        except Exception as e:
            tests.append({
                "name": "task_retrieval",
                "passed": False,
                "error": str(e)
            })
        
        # Test invalid requests
        try:
            response = self.session.post(f"{self.api_base_url}/add_task", json={"invalid": "data"})
            tests.append({
                "name": "invalid_request_handling",
                "passed": response.status_code >= 400,
                "details": {"status_code": response.status_code, "correctly_rejected": response.status_code >= 400}
            })
        except Exception as e:
            tests.append({
                "name": "invalid_request_handling",
                "passed": False,
                "error": str(e)
            })
        
        execution_time = time.time() - test_start
        passed_tests = sum(1 for test in tests if test["passed"])
        
        return {
            "overall_passed": passed_tests == len(tests),
            "tests": tests,
            "execution_time": execution_time,
            "summary": f"{passed_tests}/{len(tests)} API functionality tests passed"
        }
    
    def test_message_type_processing(self) -> Dict[str, Any]:
        """Test rich message type processing"""
        test_start = time.time()
        tests = []
        
        builder = MessageBuilder(sender="integration_test", recipient="jules")
        
        # Test different message types
        message_types = [
            ("simple_task", lambda: builder.create_simple_task("Test simple task")),
            ("complex_task", lambda: builder.create_complex_task("Test complex task", [{"step": 1, "action": "test"}])),
            ("session_start", lambda: builder.create_session_start("test_session", ["test_user"])),
            ("error_report", lambda: builder.create_error_report("TEST_ERROR", "Test error message", {"context": "test"}))
        ]
        
        for msg_type, create_func in message_types:
            try:
                message = create_func()
                
                # Convert to API format (simplified)
                api_task = {"task": f"Message type test: {msg_type} - {message.metadata.message_id}"}
                
                response = self.session.post(f"{self.api_base_url}/add_task", json=api_task)
                
                tests.append({
                    "name": f"message_type_{msg_type}",
                    "passed": response.status_code == 201,
                    "details": {
                        "message_type": msg_type,
                        "message_id": message.metadata.message_id,
                        "status_code": response.status_code
                    }
                })
            except Exception as e:
                tests.append({
                    "name": f"message_type_{msg_type}",
                    "passed": False,
                    "error": str(e)
                })
        
        execution_time = time.time() - test_start
        passed_tests = sum(1 for test in tests if test["passed"])
        
        return {
            "overall_passed": passed_tests == len(tests),
            "tests": tests,
            "execution_time": execution_time,
            "summary": f"{passed_tests}/{len(tests)} message type tests passed"
        }
    
    def test_performance_under_load(self) -> Dict[str, Any]:
        """Test system performance under load"""
        test_start = time.time()
        tests = []
        
        # Generate test load
        num_requests = 50
        tasks = self.data_generator.generate_simple_tasks(num_requests)
        
        response_times = []
        errors = []
        
        print(f"  📊 Sending {num_requests} requests...")
        
        for i, task_msg in enumerate(tasks):
            try:
                api_task = {"task": f"Load test {i+1}: {task_msg.payload.task_description}"}
                
                start_time = time.time()
                response = self.session.post(f"{self.api_base_url}/add_task", json=api_task)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                response_times.append(response_time)
                
                if response.status_code != 201:
                    errors.append(f"Request {i+1}: HTTP {response.status_code}")
                    
            except Exception as e:
                errors.append(f"Request {i+1}: {str(e)}")
        
        # Analyze performance
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            error_rate = (len(errors) / num_requests) * 100
            
            # Performance thresholds
            response_time_ok = avg_response_time < 1000  # < 1 second
            error_rate_ok = error_rate < 5  # < 5% errors
            
            tests.append({
                "name": "load_test_performance",
                "passed": response_time_ok and error_rate_ok,
                "details": {
                    "requests_sent": num_requests,
                    "avg_response_time": avg_response_time,
                    "max_response_time": max_response_time,
                    "min_response_time": min_response_time,
                    "error_count": len(errors),
                    "error_rate": error_rate,
                    "performance_acceptable": response_time_ok and error_rate_ok
                }
            })
        else:
            tests.append({
                "name": "load_test_performance",
                "passed": False,
                "error": "No successful responses received"
            })
        
        execution_time = time.time() - test_start
        passed_tests = sum(1 for test in tests if test["passed"])
        
        return {
            "overall_passed": passed_tests == len(tests),
            "tests": tests,
            "execution_time": execution_time,
            "summary": f"Load test: {avg_response_time:.0f}ms avg, {error_rate:.1f}% errors"
        }
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and recovery"""
        test_start = time.time()
        tests = []
        
        # Test various error scenarios
        error_scenarios = [
            ("empty_task", {"task": ""}),
            ("missing_task_field", {"not_task": "test"}),
            ("very_large_task", {"task": "X" * 10000}),
            ("special_characters", {"task": "Task with special chars: !@#$%^&*()"}),
            ("unicode_task", {"task": "Unicode task: 你好世界 🌍"})
        ]
        
        for scenario_name, task_data in error_scenarios:
            try:
                response = self.session.post(f"{self.api_base_url}/add_task", json=task_data)
                
                # Analyze response
                if scenario_name in ["empty_task", "missing_task_field"]:
                    # Should return error
                    expected_error = response.status_code >= 400
                    tests.append({
                        "name": f"error_handling_{scenario_name}",
                        "passed": expected_error,
                        "details": {"status_code": response.status_code, "correctly_handled": expected_error}
                    })
                else:
                    # Should handle gracefully
                    handled_gracefully = response.status_code in [200, 201]
                    tests.append({
                        "name": f"error_handling_{scenario_name}",
                        "passed": handled_gracefully,
                        "details": {"status_code": response.status_code, "handled_gracefully": handled_gracefully}
                    })
                    
            except Exception as e:
                tests.append({
                    "name": f"error_handling_{scenario_name}",
                    "passed": False,
                    "error": str(e)
                })
        
        # Test system recovery after errors
        try:
            recovery_task = {"task": "Recovery test after errors"}
            response = self.session.post(f"{self.api_base_url}/add_task", json=recovery_task)
            
            tests.append({
                "name": "system_recovery",
                "passed": response.status_code == 201,
                "details": {"status_code": response.status_code, "recovery_successful": response.status_code == 201}
            })
        except Exception as e:
            tests.append({
                "name": "system_recovery",
                "passed": False,
                "error": str(e)
            })
        
        execution_time = time.time() - test_start
        passed_tests = sum(1 for test in tests if test["passed"])
        
        return {
            "overall_passed": passed_tests == len(tests),
            "tests": tests,
            "execution_time": execution_time,
            "summary": f"{passed_tests}/{len(tests)} error handling tests passed"
        }
    
    def test_monitoring_integration(self) -> Dict[str, Any]:
        """Test monitoring and dashboard integration"""
        test_start = time.time()
        tests = []
        
        # Test dashboard API endpoints
        dashboard_endpoints = [
            ("/api/dashboard-data", "dashboard_data"),
            ("/api/system-status", "system_status"),
            ("/api/alerts", "alerts")
        ]
        
        for endpoint, test_name in dashboard_endpoints:
            try:
                response = requests.get(f"{self.dashboard_url}{endpoint}", timeout=5)
                tests.append({
                    "name": f"dashboard_{test_name}",
                    "passed": response.status_code == 200,
                    "details": {"endpoint": endpoint, "status_code": response.status_code}
                })
            except Exception as e:
                tests.append({
                    "name": f"dashboard_{test_name}",
                    "passed": False,
                    "error": str(e)
                })
        
        # Test monitoring data collection
        try:
            # Generate some activity
            test_task = {"task": "Monitoring integration test"}
            self.session.post(f"{self.api_base_url}/add_task", json=test_task)
            
            # Wait a moment for monitoring to collect data
            time.sleep(2)
            
            # Check if monitoring data is being collected
            response = requests.get(f"{self.dashboard_url}/api/dashboard-data", timeout=5)
            if response.status_code == 200:
                data = response.json()
                monitoring_active = "system_status" in data and data["system_status"].get("status") == "healthy"
                
                tests.append({
                    "name": "monitoring_data_collection",
                    "passed": monitoring_active,
                    "details": {"monitoring_active": monitoring_active, "data_available": bool(data)}
                })
            else:
                tests.append({
                    "name": "monitoring_data_collection",
                    "passed": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            tests.append({
                "name": "monitoring_data_collection",
                "passed": False,
                "error": str(e)
            })
        
        execution_time = time.time() - test_start
        passed_tests = sum(1 for test in tests if test["passed"])
        
        return {
            "overall_passed": passed_tests == len(tests),
            "tests": tests,
            "execution_time": execution_time,
            "summary": f"{passed_tests}/{len(tests)} monitoring integration tests passed"
        }
    
    def test_analytics_optimization(self) -> Dict[str, Any]:
        """Test analytics and optimization components"""
        test_start = time.time()
        tests = []
        
        # Test performance analyzer
        try:
            # Generate some test metrics
            test_metrics = []
            for i in range(10):
                metric = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "api_health": {"status": "healthy", "response_time": 100 + i * 10},
                    "system_resources": {"cpu_percent": 50 + i},
                    "task_queue": {"total_tasks": i}
                }
                test_metrics.append(metric)
            
            analysis = self.analyzer.analyze_performance_trends(test_metrics)
            
            tests.append({
                "name": "performance_analysis",
                "passed": "response_time_analysis" in analysis,
                "details": {"analysis_keys": list(analysis.keys())}
            })
        except Exception as e:
            tests.append({
                "name": "performance_analysis",
                "passed": False,
                "error": str(e)
            })
        
        # Test baseline establishment
        try:
            baseline_result = self.baseline.establish_baseline(test_metrics)
            
            tests.append({
                "name": "baseline_establishment",
                "passed": "response_time" in baseline_result,
                "details": {"baseline_keys": list(baseline_result.keys())}
            })
        except Exception as e:
            tests.append({
                "name": "baseline_establishment",
                "passed": False,
                "error": str(e)
            })
        
        # Test optimization engine
        try:
            optimization_result = self.optimizer.analyze_and_optimize(test_metrics)
            
            tests.append({
                "name": "optimization_engine",
                "passed": "analysis_results" in optimization_result,
                "details": {"optimization_keys": list(optimization_result.keys())}
            })
        except Exception as e:
            tests.append({
                "name": "optimization_engine",
                "passed": False,
                "error": str(e)
            })
        
        execution_time = time.time() - test_start
        passed_tests = sum(1 for test in tests if test["passed"])
        
        return {
            "overall_passed": passed_tests == len(tests),
            "tests": tests,
            "execution_time": execution_time,
            "summary": f"{passed_tests}/{len(tests)} analytics & optimization tests passed"
        }
    
    def test_end_to_end_workflows(self) -> Dict[str, Any]:
        """Test complete end-to-end workflows"""
        test_start = time.time()
        tests = []
        
        # Test complete task workflow
        try:
            workflow_id = f"e2e_workflow_{int(time.time())}"
            
            # Step 1: Create task
            task_data = {"task": f"End-to-end workflow test: {workflow_id}"}
            create_response = self.session.post(f"{self.api_base_url}/add_task", json=task_data)
            
            # Step 2: Verify task exists
            list_response = self.session.get(f"{self.api_base_url}/tasks")
            tasks = list_response.json() if list_response.status_code == 200 else []
            
            # Step 3: Check if our task is in the list
            workflow_task_found = any(workflow_id in task.get("task", "") for task in tasks)
            
            workflow_success = (
                create_response.status_code == 201 and
                list_response.status_code == 200 and
                workflow_task_found
            )
            
            tests.append({
                "name": "end_to_end_task_workflow",
                "passed": workflow_success,
                "details": {
                    "workflow_id": workflow_id,
                    "create_status": create_response.status_code,
                    "list_status": list_response.status_code,
                    "task_found": workflow_task_found,
                    "total_tasks": len(tasks)
                }
            })
        except Exception as e:
            tests.append({
                "name": "end_to_end_task_workflow",
                "passed": False,
                "error": str(e)
            })
        
        # Test monitoring workflow
        try:
            # Generate activity
            for i in range(3):
                self.session.post(f"{self.api_base_url}/add_task", json={"task": f"Monitoring workflow test {i+1}"})
            
            # Check monitoring response
            monitoring_response = requests.get(f"{self.dashboard_url}/api/dashboard-data", timeout=5)
            
            monitoring_workflow_success = monitoring_response.status_code == 200
            
            tests.append({
                "name": "end_to_end_monitoring_workflow",
                "passed": monitoring_workflow_success,
                "details": {"monitoring_status": monitoring_response.status_code}
            })
        except Exception as e:
            tests.append({
                "name": "end_to_end_monitoring_workflow",
                "passed": False,
                "error": str(e)
            })
        
        execution_time = time.time() - test_start
        passed_tests = sum(1 for test in tests if test["passed"])
        
        return {
            "overall_passed": passed_tests == len(tests),
            "tests": tests,
            "execution_time": execution_time,
            "summary": f"{passed_tests}/{len(tests)} end-to-end workflow tests passed"
        }
    
    def test_stress_scenarios(self) -> Dict[str, Any]:
        """Test system under stress conditions"""
        test_start = time.time()
        tests = []
        
        # Concurrent request stress test
        try:
            num_threads = 5
            requests_per_thread = 10
            
            results = {"successes": 0, "errors": 0, "response_times": []}
            results_lock = threading.Lock()
            
            def stress_worker(thread_id):
                for i in range(requests_per_thread):
                    try:
                        task_data = {"task": f"Stress test T{thread_id}-R{i+1}"}
                        
                        start_time = time.time()
                        response = self.session.post(f"{self.api_base_url}/add_task", json=task_data)
                        response_time = (time.time() - start_time) * 1000
                        
                        with results_lock:
                            if response.status_code == 201:
                                results["successes"] += 1
                            else:
                                results["errors"] += 1
                            results["response_times"].append(response_time)
                            
                    except Exception:
                        with results_lock:
                            results["errors"] += 1
            
            # Run concurrent threads
            threads = []
            for i in range(num_threads):
                thread = threading.Thread(target=stress_worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            total_requests = num_threads * requests_per_thread
            success_rate = (results["successes"] / total_requests) * 100
            avg_response_time = statistics.mean(results["response_times"]) if results["response_times"] else 0
            
            stress_test_passed = success_rate > 90 and avg_response_time < 2000  # 90% success, < 2s response
            
            tests.append({
                "name": "concurrent_stress_test",
                "passed": stress_test_passed,
                "details": {
                    "total_requests": total_requests,
                    "successes": results["successes"],
                    "errors": results["errors"],
                    "success_rate": success_rate,
                    "avg_response_time": avg_response_time,
                    "max_response_time": max(results["response_times"]) if results["response_times"] else 0
                }
            })
        except Exception as e:
            tests.append({
                "name": "concurrent_stress_test",
                "passed": False,
                "error": str(e)
            })
        
        execution_time = time.time() - test_start
        passed_tests = sum(1 for test in tests if test["passed"])
        
        return {
            "overall_passed": passed_tests == len(tests),
            "tests": tests,
            "execution_time": execution_time,
            "summary": f"Stress test: {success_rate:.1f}% success rate, {avg_response_time:.0f}ms avg"
        }
    
    def test_data_persistence(self) -> Dict[str, Any]:
        """Test data persistence and integrity"""
        test_start = time.time()
        tests = []
        
        # Test task persistence
        try:
            # Get initial task count
            initial_response = self.session.get(f"{self.api_base_url}/tasks")
            initial_tasks = initial_response.json() if initial_response.status_code == 200 else []
            initial_count = len(initial_tasks)
            
            # Add test tasks
            test_tasks = ["Persistence test 1", "Persistence test 2", "Persistence test 3"]
            for task_desc in test_tasks:
                self.session.post(f"{self.api_base_url}/add_task", json={"task": task_desc})
            
            # Verify tasks were added
            final_response = self.session.get(f"{self.api_base_url}/tasks")
            final_tasks = final_response.json() if final_response.status_code == 200 else []
            final_count = len(final_tasks)
            
            persistence_success = (final_count - initial_count) == len(test_tasks)
            
            tests.append({
                "name": "task_persistence",
                "passed": persistence_success,
                "details": {
                    "initial_count": initial_count,
                    "final_count": final_count,
                    "tasks_added": len(test_tasks),
                    "persistence_verified": persistence_success
                }
            })
        except Exception as e:
            tests.append({
                "name": "task_persistence",
                "passed": False,
                "error": str(e)
            })
        
        execution_time = time.time() - test_start
        passed_tests = sum(1 for test in tests if test["passed"])
        
        return {
            "overall_passed": passed_tests == len(tests),
            "tests": tests,
            "execution_time": execution_time,
            "summary": f"{passed_tests}/{len(tests)} data persistence tests passed"
        }
    
    def _print_test_summary(self, results: Dict[str, Any]):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🏁 A2A INTEGRATION TEST SUITE COMPLETE")
        print("=" * 60)
        
        summary = results["overall_summary"]
        
        print(f"📊 Overall Results:")
        print(f"   Categories: {summary['passed_categories']}/{summary['total_categories']} passed ({summary['category_success_rate']:.1f}%)")
        print(f"   Individual Tests: {summary['passed_tests']}/{summary['total_tests']} passed ({summary['success_rate']:.1f}%)")
        print(f"   Execution Time: {results['total_execution_time']:.1f} seconds")
        
        # Category breakdown
        print(f"\n📋 Category Results:")
        for category in results["test_categories"]:
            status = "✅ PASS" if category.get("overall_passed", False) else "❌ FAIL"
            test_count = len(category.get("tests", []))
            passed_count = sum(1 for test in category.get("tests", []) if test.get("passed", False))
            print(f"   {status} {category['category_name']}: {passed_count}/{test_count}")
        
        # Overall assessment
        if summary["success_rate"] >= 95:
            print(f"\n🎉 EXCELLENT: System performing at {summary['success_rate']:.1f}% - Ready for production!")
        elif summary["success_rate"] >= 85:
            print(f"\n✅ GOOD: System performing at {summary['success_rate']:.1f}% - Minor improvements needed")
        elif summary["success_rate"] >= 70:
            print(f"\n⚠️ ACCEPTABLE: System performing at {summary['success_rate']:.1f}% - Several issues need attention")
        else:
            print(f"\n🚨 POOR: System performing at {summary['success_rate']:.1f}% - Major issues require immediate attention")
    
    def _save_test_results(self, results: Dict[str, Any]):
        """Save test results to file"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        results_file = Path(f"integration_test_results_{timestamp}.json")
        
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n📄 Integration test results saved to: {results_file}")
        except Exception as e:
            print(f"\n⚠️ Failed to save test results: {e}")


if __name__ == "__main__":
    print("🧪 A2A System Integration Test Suite")
    print("=" * 50)
    
    # Run integration tests
    test_suite = IntegrationTestSuite()
    results = test_suite.run_full_integration_test()
    
    print(f"\n🎯 Integration testing complete!")
    print(f"Final Score: {results['overall_summary']['success_rate']:.1f}%")