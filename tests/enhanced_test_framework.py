"""
Enhanced A2A Testing Framework
Comprehensive testing system for Agent-to-Agent communication
"""

import pytest
import asyncio
import time
import json
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import signal
import threading
from contextlib import contextmanager

from shared.message_types import A2AMessage, MessageType, TaskStatus, validate_message_schema
from tests.test_data_generator import TestDataGenerator


class A2ATestFramework:
    """Enhanced testing framework for A2A system"""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:5000"):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.test_results = []
        self.metrics = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "avg_response_time": 0.0,
            "max_response_time": 0.0,
            "min_response_time": float('inf'),
            "error_rate": 0.0
        }
        self.data_generator = TestDataGenerator()
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """Verify API server is running and responsive"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.api_base_url}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                health_data['response_time'] = response_time
                return True, health_data
            else:
                return False, {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return False, {"error": str(e)}
    
    def test_basic_functionality(self) -> Dict[str, Any]:
        """Test basic API functionality"""
        results = {
            "test_name": "basic_functionality",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "subtests": []
        }
        
        # Test 1: Health check
        health_ok, health_data = self.health_check()
        results["subtests"].append({
            "name": "health_check",
            "passed": health_ok,
            "data": health_data
        })
        
        # Test 2: Add simple task
        try:
            task_data = {"task": "Test task from enhanced framework"}
            start_time = time.time()
            response = self.session.post(f"{self.api_base_url}/add_task", json=task_data)
            response_time = time.time() - start_time
            
            add_task_passed = response.status_code == 201
            results["subtests"].append({
                "name": "add_task",
                "passed": add_task_passed,
                "data": {
                    "status_code": response.status_code,
                    "response": response.json() if add_task_passed else response.text,
                    "response_time": response_time
                }
            })
        except Exception as e:
            results["subtests"].append({
                "name": "add_task",
                "passed": False,
                "data": {"error": str(e)}
            })
        
        # Test 3: List tasks
        try:
            start_time = time.time()
            response = self.session.get(f"{self.api_base_url}/tasks")
            response_time = time.time() - start_time
            
            list_tasks_passed = response.status_code == 200
            results["subtests"].append({
                "name": "list_tasks",
                "passed": list_tasks_passed,
                "data": {
                    "status_code": response.status_code,
                    "response": response.json() if list_tasks_passed else response.text,
                    "response_time": response_time,
                    "task_count": len(response.json()) if list_tasks_passed else 0
                }
            })
        except Exception as e:
            results["subtests"].append({
                "name": "list_tasks",
                "passed": False,
                "data": {"error": str(e)}
            })
        
        # Calculate overall success
        passed_subtests = sum(1 for test in results["subtests"] if test["passed"])
        results["overall_passed"] = passed_subtests == len(results["subtests"])
        results["success_rate"] = passed_subtests / len(results["subtests"]) * 100
        
        return results
    
    def test_message_types(self) -> Dict[str, Any]:
        """Test rich message type handling"""
        results = {
            "test_name": "message_types",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "subtests": []
        }
        
        # Test different message types
        test_messages = [
            self.data_generator.generate_simple_tasks(1)[0],
            self.data_generator.generate_complex_tasks(1)[0],
            self.data_generator.generate_priority_tasks(1)[0],
        ]
        
        for i, msg in enumerate(test_messages):
            try:
                # Convert A2AMessage to task format for current API
                task_data = {"task": f"Message Type Test {i+1}: {msg.metadata.message_type.value}"}
                
                start_time = time.time()
                response = self.session.post(f"{self.api_base_url}/add_task", json=task_data)
                response_time = time.time() - start_time
                
                passed = response.status_code == 201
                results["subtests"].append({
                    "name": f"message_type_{msg.metadata.message_type.value}",
                    "passed": passed,
                    "data": {
                        "message_type": msg.metadata.message_type.value,
                        "response_time": response_time,
                        "status_code": response.status_code
                    }
                })
            except Exception as e:
                results["subtests"].append({
                    "name": f"message_type_{msg.metadata.message_type.value}",
                    "passed": False,
                    "data": {"error": str(e)}
                })
        
        # Calculate overall success
        passed_subtests = sum(1 for test in results["subtests"] if test["passed"])
        results["overall_passed"] = passed_subtests == len(results["subtests"])
        results["success_rate"] = passed_subtests / len(results["subtests"]) * 100
        
        return results
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling scenarios"""
        results = {
            "test_name": "error_handling",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "subtests": []
        }
        
        # Test invalid requests
        error_tests = [
            {"name": "empty_task", "data": {"task": ""}},
            {"name": "missing_task_field", "data": {"not_task": "test"}},
            {"name": "invalid_json", "data": "not json"},
            {"name": "very_long_task", "data": {"task": "A" * 10000}},
        ]
        
        for test_case in error_tests:
            try:
                if test_case["name"] == "invalid_json":
                    # Send raw string instead of JSON
                    response = self.session.post(
                        f"{self.api_base_url}/add_task",
                        data=test_case["data"],
                        headers={"Content-Type": "application/json"}
                    )
                else:
                    response = self.session.post(f"{self.api_base_url}/add_task", json=test_case["data"])
                
                # For error tests, we expect error status codes
                expected_error = test_case["name"] in ["empty_task", "missing_task_field", "invalid_json"]
                passed = (response.status_code >= 400) == expected_error
                
                results["subtests"].append({
                    "name": test_case["name"],
                    "passed": passed,
                    "data": {
                        "status_code": response.status_code,
                        "expected_error": expected_error,
                        "response": response.text[:200]  # First 200 chars
                    }
                })
            except Exception as e:
                results["subtests"].append({
                    "name": test_case["name"],
                    "passed": False,
                    "data": {"error": str(e)}
                })
        
        # Calculate overall success
        passed_subtests = sum(1 for test in results["subtests"] if test["passed"])
        results["overall_passed"] = passed_subtests == len(results["subtests"])
        results["success_rate"] = passed_subtests / len(results["subtests"]) * 100
        
        return results
    
    def test_performance(self, num_requests: int = 50) -> Dict[str, Any]:
        """Test API performance under load"""
        results = {
            "test_name": "performance",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "num_requests": num_requests,
            "response_times": [],
            "errors": []
        }
        
        # Generate test data
        tasks = self.data_generator.generate_simple_tasks(num_requests)
        
        start_time = time.time()
        
        for i, task_msg in enumerate(tasks):
            try:
                task_data = {"task": f"Performance test {i+1}: {task_msg.payload.task_description}"}
                
                req_start = time.time()
                response = self.session.post(f"{self.api_base_url}/add_task", json=task_data)
                req_time = time.time() - req_start
                
                results["response_times"].append(req_time)
                
                if response.status_code != 201:
                    results["errors"].append({
                        "request_num": i+1,
                        "status_code": response.status_code,
                        "error": response.text[:100]
                    })
                
            except Exception as e:
                results["errors"].append({
                    "request_num": i+1,
                    "error": str(e)
                })
        
        total_time = time.time() - start_time
        response_times = results["response_times"]
        
        # Calculate performance metrics
        results["metrics"] = {
            "total_time": total_time,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "requests_per_second": num_requests / total_time if total_time > 0 else 0,
            "error_rate": len(results["errors"]) / num_requests * 100,
            "success_rate": (num_requests - len(results["errors"])) / num_requests * 100
        }
        
        results["overall_passed"] = results["metrics"]["error_rate"] < 5  # Less than 5% error rate
        
        return results
    
    def test_concurrent_access(self, num_threads: int = 5, requests_per_thread: int = 10) -> Dict[str, Any]:
        """Test concurrent access to API"""
        results = {
            "test_name": "concurrent_access",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "num_threads": num_threads,
            "requests_per_thread": requests_per_thread,
            "thread_results": [],
            "errors": []
        }
        
        def worker_thread(thread_id: int, num_requests: int):
            """Worker thread for concurrent testing"""
            thread_results = {
                "thread_id": thread_id,
                "requests_completed": 0,
                "errors": [],
                "response_times": []
            }
            
            session = requests.Session()
            session.headers.update({"Content-Type": "application/json"})
            
            for i in range(num_requests):
                try:
                    task_data = {"task": f"Concurrent test T{thread_id}-R{i+1}"}
                    
                    start_time = time.time()
                    response = session.post(f"{self.api_base_url}/add_task", json=task_data)
                    response_time = time.time() - start_time
                    
                    thread_results["response_times"].append(response_time)
                    
                    if response.status_code == 201:
                        thread_results["requests_completed"] += 1
                    else:
                        thread_results["errors"].append({
                            "request": i+1,
                            "status_code": response.status_code,
                            "error": response.text[:100]
                        })
                        
                except Exception as e:
                    thread_results["errors"].append({
                        "request": i+1,
                        "error": str(e)
                    })
            
            return thread_results
        
        # Run concurrent threads
        threads = []
        thread_results = {}
        
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(
                target=lambda tid=i: thread_results.update({tid: worker_thread(tid, requests_per_thread)})
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Compile results
        results["thread_results"] = list(thread_results.values())
        
        total_requests = num_threads * requests_per_thread
        total_completed = sum(tr["requests_completed"] for tr in results["thread_results"])
        total_errors = sum(len(tr["errors"]) for tr in results["thread_results"])
        
        all_response_times = []
        for tr in results["thread_results"]:
            all_response_times.extend(tr["response_times"])
        
        results["metrics"] = {
            "total_time": total_time,
            "total_requests": total_requests,
            "total_completed": total_completed,
            "total_errors": total_errors,
            "success_rate": (total_completed / total_requests) * 100 if total_requests > 0 else 0,
            "avg_response_time": sum(all_response_times) / len(all_response_times) if all_response_times else 0,
            "requests_per_second": total_completed / total_time if total_time > 0 else 0
        }
        
        results["overall_passed"] = results["metrics"]["success_rate"] > 95  # 95% success rate
        
        return results
    
    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite"""
        suite_results = {
            "test_suite": "comprehensive_a2a_testing",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tests": [],
            "summary": {}
        }
        
        print("🧪 Starting comprehensive A2A test suite...")
        
        # Run all test categories
        test_methods = [
            ("Basic Functionality", self.test_basic_functionality),
            ("Message Types", self.test_message_types),
            ("Error Handling", self.test_error_handling),
            ("Performance", lambda: self.test_performance(30)),
            ("Concurrent Access", lambda: self.test_concurrent_access(3, 5))
        ]
        
        for test_name, test_method in test_methods:
            print(f"  Running {test_name}...")
            try:
                test_result = test_method()
                suite_results["tests"].append(test_result)
                print(f"    ✅ {test_name}: {'PASSED' if test_result['overall_passed'] else 'FAILED'}")
            except Exception as e:
                error_result = {
                    "test_name": test_name.lower().replace(" ", "_"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "overall_passed": False,
                    "error": str(e)
                }
                suite_results["tests"].append(error_result)
                print(f"    ❌ {test_name}: ERROR - {str(e)}")
        
        # Calculate summary
        total_tests = len(suite_results["tests"])
        passed_tests = sum(1 for test in suite_results["tests"] if test["overall_passed"])
        
        suite_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "overall_passed": passed_tests == total_tests
        }
        
        print(f"\n📊 Test Suite Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {suite_results['summary']['success_rate']:.1f}%")
        
        return suite_results
    
    def save_results(self, results: Dict[str, Any], filename: str) -> None:
        """Save test results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📄 Results saved to {filename}")


@contextmanager
def api_server_context(server_script: str = "api/jules_server.py"):
    """Context manager for running API server during tests"""
    server_process = None
    try:
        # Start server
        server_process = subprocess.Popen(
            ["python", server_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(2)
        
        # Check if server is running
        test_framework = A2ATestFramework()
        health_ok, _ = test_framework.health_check()
        
        if not health_ok:
            raise Exception("API server failed to start or is not responding")
        
        yield server_process
        
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()


# Example usage and main execution
if __name__ == "__main__":
    # Run tests with server auto-start
    try:
        with api_server_context():
            framework = A2ATestFramework()
            results = framework.run_comprehensive_test_suite()
            
            # Save results
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
            framework.save_results(results, filename)
            
            print(f"\n🎯 Testing complete! Overall result: {'PASSED' if results['summary']['overall_passed'] else 'FAILED'}")
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        print("🔧 Make sure the API server can be started and is accessible")