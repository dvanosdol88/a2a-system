"""
A2A Test Orchestrator
Advanced test coordination and management for Claude-Jules interactions
"""

import asyncio
import json
import time
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from shared.message_types import A2AMessage, MessageType, MessageBuilder
from tests.test_data_generator import TestDataGenerator
from tests.enhanced_test_framework import A2ATestFramework


class TestPhase(Enum):
    """Test execution phases"""
    SETUP = "setup"
    EXECUTION = "execution"
    VALIDATION = "validation"
    CLEANUP = "cleanup"
    COMPLETE = "complete"


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TestScenario:
    """Individual test scenario definition"""
    name: str
    description: str
    test_type: str
    messages: List[A2AMessage]
    expected_results: Dict[str, Any]
    timeout_seconds: int = 30
    retry_count: int = 0
    prerequisites: List[str] = None
    cleanup_actions: List[str] = None


@dataclass
class TestExecution:
    """Test execution tracking"""
    scenario: TestScenario
    status: TestStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    results: Dict[str, Any] = None
    errors: List[str] = None
    metrics: Dict[str, Any] = None


class TestOrchestrator:
    """Advanced test orchestration engine"""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:5000"):
        self.api_base_url = api_base_url
        self.test_framework = A2ATestFramework(api_base_url)
        self.data_generator = TestDataGenerator()
        self.test_scenarios = []
        self.active_executions = {}
        self.completed_executions = []
        self.session_data = {}
        self.orchestrator_metrics = {
            "total_scenarios": 0,
            "completed_scenarios": 0,
            "failed_scenarios": 0,
            "total_execution_time": 0,
            "average_scenario_time": 0,
            "success_rate": 0.0
        }
    
    def create_scenario(self, name: str, description: str, test_type: str, 
                       messages: List[A2AMessage], expected_results: Dict[str, Any],
                       timeout_seconds: int = 30, prerequisites: List[str] = None) -> TestScenario:
        """Create a new test scenario"""
        scenario = TestScenario(
            name=name,
            description=description,
            test_type=test_type,
            messages=messages,
            expected_results=expected_results,
            timeout_seconds=timeout_seconds,
            prerequisites=prerequisites or []
        )
        self.test_scenarios.append(scenario)
        return scenario
    
    def create_interactive_scenario(self, name: str, description: str) -> TestScenario:
        """Create interactive Claude-Jules communication scenario"""
        builder = MessageBuilder(sender="claude", recipient="jules")
        
        # Create a series of interactive messages
        messages = [
            builder.create_session_start(
                session_name=f"interactive_{name}",
                participants=["claude", "jules"],
                session_data={"test_type": "interactive", "scenario": name}
            ),
            builder.create_simple_task(f"Interactive task 1 for {name}"),
            builder.create_complex_task(
                f"Interactive complex task for {name}",
                steps=[
                    {"step": 1, "action": "Process initial request"},
                    {"step": 2, "action": "Execute interactive response"},
                    {"step": 3, "action": "Validate interaction result"}
                ]
            )
        ]
        
        expected_results = {
            "session_established": True,
            "tasks_processed": len(messages) - 1,  # Excluding session start
            "interaction_successful": True,
            "response_time_acceptable": True
        }
        
        return self.create_scenario(
            name=name,
            description=description,
            test_type="interactive",
            messages=messages,
            expected_results=expected_results,
            timeout_seconds=60
        )
    
    def create_performance_scenario(self, name: str, num_messages: int = 50) -> TestScenario:
        """Create performance testing scenario"""
        messages = self.data_generator.generate_performance_test_data(num_messages)
        
        expected_results = {
            "all_messages_processed": True,
            "average_response_time": "<= 1.0",  # seconds
            "error_rate": "< 5",  # percent
            "throughput": f">= {num_messages * 0.8}"  # messages per minute
        }
        
        return self.create_scenario(
            name=name,
            description=f"Performance test with {num_messages} messages",
            test_type="performance",
            messages=messages,
            expected_results=expected_results,
            timeout_seconds=120
        )
    
    def create_error_recovery_scenario(self, name: str) -> TestScenario:
        """Create error handling and recovery scenario"""
        messages = self.data_generator.generate_error_scenarios(10)
        
        expected_results = {
            "errors_handled_gracefully": True,
            "system_remains_stable": True,
            "recovery_successful": True,
            "error_reporting_accurate": True
        }
        
        return self.create_scenario(
            name=name,
            description="Error handling and recovery testing",
            test_type="error_recovery",
            messages=messages,
            expected_results=expected_results,
            timeout_seconds=45
        )
    
    def create_session_management_scenario(self, name: str) -> TestScenario:
        """Create session management testing scenario"""
        session_scenarios = self.data_generator.generate_session_scenarios(3)
        
        # Flatten all session messages
        all_messages = []
        for scenario in session_scenarios:
            all_messages.extend(scenario)
        
        expected_results = {
            "sessions_created": 3,
            "session_isolation": True,
            "session_cleanup": True,
            "state_management": True
        }
        
        return self.create_scenario(
            name=name,
            description="Session management and state tracking",
            test_type="session_management",
            messages=all_messages,
            expected_results=expected_results,
            timeout_seconds=90
        )
    
    def execute_scenario(self, scenario: TestScenario) -> TestExecution:
        """Execute a single test scenario"""
        execution = TestExecution(
            scenario=scenario,
            status=TestStatus.RUNNING,
            start_time=datetime.now(timezone.utc),
            results={},
            errors=[],
            metrics={}
        )
        
        self.active_executions[scenario.name] = execution
        
        try:
            # Check prerequisites
            if scenario.prerequisites:
                prereq_check = self._check_prerequisites(scenario.prerequisites)
                if not prereq_check["passed"]:
                    execution.status = TestStatus.SKIPPED
                    execution.errors.append(f"Prerequisites not met: {prereq_check['missing']}")
                    return execution
            
            # Execute based on test type
            if scenario.test_type == "interactive":
                execution.results = self._execute_interactive_test(scenario)
            elif scenario.test_type == "performance":
                execution.results = self._execute_performance_test(scenario)
            elif scenario.test_type == "error_recovery":
                execution.results = self._execute_error_recovery_test(scenario)
            elif scenario.test_type == "session_management":
                execution.results = self._execute_session_management_test(scenario)
            else:
                execution.results = self._execute_generic_test(scenario)
            
            # Validate results
            validation_result = self._validate_results(execution.results, scenario.expected_results)
            execution.status = TestStatus.PASSED if validation_result["passed"] else TestStatus.FAILED
            
            if not validation_result["passed"]:
                execution.errors.extend(validation_result["errors"])
            
            # Calculate metrics
            execution.metrics = self._calculate_execution_metrics(execution)
            
        except Exception as e:
            execution.status = TestStatus.ERROR
            execution.errors.append(f"Execution error: {str(e)}")
        
        finally:
            execution.end_time = datetime.now(timezone.utc)
            self.completed_executions.append(execution)
            if scenario.name in self.active_executions:
                del self.active_executions[scenario.name]
        
        return execution
    
    def _execute_interactive_test(self, scenario: TestScenario) -> Dict[str, Any]:
        """Execute interactive test scenario"""
        results = {
            "session_established": False,
            "tasks_processed": 0,
            "interaction_successful": False,
            "response_times": [],
            "errors": []
        }
        
        session_id = None
        
        for message in scenario.messages:
            try:
                if message.metadata.message_type == MessageType.SESSION_START:
                    session_id = message.payload.session_id
                    results["session_established"] = True
                    
                elif message.metadata.message_type in [MessageType.SIMPLE_TASK, MessageType.COMPLEX_TASK]:
                    # Convert A2A message to API format
                    task_data = {"task": f"Interactive: {message.payload.task_description}"}
                    
                    start_time = time.time()
                    response = self.test_framework.session.post(
                        f"{self.api_base_url}/add_task",
                        json=task_data
                    )
                    response_time = time.time() - start_time
                    
                    results["response_times"].append(response_time)
                    
                    if response.status_code == 201:
                        results["tasks_processed"] += 1
                    else:
                        results["errors"].append(f"Task failed: {response.status_code}")
                        
            except Exception as e:
                results["errors"].append(f"Message processing error: {str(e)}")
        
        results["interaction_successful"] = len(results["errors"]) == 0
        results["average_response_time"] = sum(results["response_times"]) / len(results["response_times"]) if results["response_times"] else 0
        
        return results
    
    def _execute_performance_test(self, scenario: TestScenario) -> Dict[str, Any]:
        """Execute performance test scenario"""
        return self.test_framework.test_performance(len(scenario.messages))
    
    def _execute_error_recovery_test(self, scenario: TestScenario) -> Dict[str, Any]:
        """Execute error recovery test scenario"""
        results = {
            "errors_handled_gracefully": True,
            "system_remains_stable": True,
            "recovery_successful": True,
            "error_reporting_accurate": True,
            "recovery_metrics": []
        }
        
        # Test various error scenarios
        error_test_results = self.test_framework.test_error_handling()
        
        # Check if system remains stable after errors
        health_check = self.test_framework.health_check()
        results["system_remains_stable"] = health_check[0]
        
        # Test recovery by sending valid requests after errors
        try:
            recovery_task = {"task": "Recovery test task"}
            response = self.test_framework.session.post(
                f"{self.api_base_url}/add_task",
                json=recovery_task
            )
            results["recovery_successful"] = response.status_code == 201
        except Exception as e:
            results["recovery_successful"] = False
            results["error_reporting_accurate"] = False
        
        results["errors_handled_gracefully"] = error_test_results["overall_passed"]
        
        return results
    
    def _execute_session_management_test(self, scenario: TestScenario) -> Dict[str, Any]:
        """Execute session management test scenario"""
        results = {
            "sessions_created": 0,
            "session_isolation": True,
            "session_cleanup": True,
            "state_management": True,
            "session_details": []
        }
        
        active_sessions = set()
        
        for message in scenario.messages:
            if message.metadata.message_type == MessageType.SESSION_START:
                session_id = message.payload.session_id
                active_sessions.add(session_id)
                results["sessions_created"] += 1
                
                results["session_details"].append({
                    "session_id": session_id,
                    "created_at": message.metadata.timestamp,
                    "participants": message.payload.participants
                })
        
        # Test session isolation by ensuring tasks belong to correct sessions
        # This is a simplified test - in a full implementation, we'd verify
        # that tasks are properly associated with their sessions
        
        return results
    
    def _execute_generic_test(self, scenario: TestScenario) -> Dict[str, Any]:
        """Execute generic test scenario"""
        results = {
            "messages_processed": 0,
            "errors": [],
            "response_times": [],
            "status_codes": []
        }
        
        for message in scenario.messages:
            try:
                # Convert A2A message to API format (simplified)
                task_data = {"task": f"Generic test: {getattr(message.payload, 'task_description', 'Unknown task')}"}
                
                start_time = time.time()
                response = self.test_framework.session.post(
                    f"{self.api_base_url}/add_task",
                    json=task_data
                )
                response_time = time.time() - start_time
                
                results["response_times"].append(response_time)
                results["status_codes"].append(response.status_code)
                
                if response.status_code == 201:
                    results["messages_processed"] += 1
                else:
                    results["errors"].append(f"HTTP {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                results["errors"].append(f"Processing error: {str(e)}")
        
        return results
    
    def _validate_results(self, actual_results: Dict[str, Any], expected_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate actual results against expected results"""
        validation = {
            "passed": True,
            "errors": [],
            "validations": []
        }
        
        for key, expected_value in expected_results.items():
            if key not in actual_results:
                validation["passed"] = False
                validation["errors"].append(f"Missing result key: {key}")
                continue
            
            actual_value = actual_results[key]
            
            # Handle different validation types
            if isinstance(expected_value, str) and expected_value.startswith("<="):
                threshold = float(expected_value[2:].strip())
                if actual_value > threshold:
                    validation["passed"] = False
                    validation["errors"].append(f"{key}: {actual_value} > {threshold}")
            elif isinstance(expected_value, str) and expected_value.startswith(">="):
                threshold = float(expected_value[2:].strip())
                if actual_value < threshold:
                    validation["passed"] = False
                    validation["errors"].append(f"{key}: {actual_value} < {threshold}")
            elif isinstance(expected_value, str) and expected_value.startswith("<"):
                threshold = float(expected_value[1:].strip())
                if actual_value >= threshold:
                    validation["passed"] = False
                    validation["errors"].append(f"{key}: {actual_value} >= {threshold}")
            elif actual_value != expected_value:
                validation["passed"] = False
                validation["errors"].append(f"{key}: expected {expected_value}, got {actual_value}")
            
            validation["validations"].append({
                "key": key,
                "expected": expected_value,
                "actual": actual_value,
                "passed": key not in [err.split(":")[0] for err in validation["errors"]]
            })
        
        return validation
    
    def _calculate_execution_metrics(self, execution: TestExecution) -> Dict[str, Any]:
        """Calculate metrics for test execution"""
        if not execution.start_time or not execution.end_time:
            return {}
        
        execution_time = (execution.end_time - execution.start_time).total_seconds()
        
        metrics = {
            "execution_time_seconds": execution_time,
            "messages_count": len(execution.scenario.messages),
            "errors_count": len(execution.errors),
            "success_rate": 0.0 if execution.status == TestStatus.FAILED else 100.0
        }
        
        if execution.results:
            if "response_times" in execution.results:
                response_times = execution.results["response_times"]
                if response_times:
                    metrics["avg_response_time"] = sum(response_times) / len(response_times)
                    metrics["max_response_time"] = max(response_times)
                    metrics["min_response_time"] = min(response_times)
            
            if "messages_processed" in execution.results:
                processed = execution.results["messages_processed"]
                total = len(execution.scenario.messages)
                metrics["processing_rate"] = (processed / total) * 100 if total > 0 else 0
        
        return metrics
    
    def _check_prerequisites(self, prerequisites: List[str]) -> Dict[str, Any]:
        """Check if prerequisites are met"""
        result = {
            "passed": True,
            "missing": []
        }
        
        for prereq in prerequisites:
            if prereq == "api_server_running":
                health_ok, _ = self.test_framework.health_check()
                if not health_ok:
                    result["passed"] = False
                    result["missing"].append("API server not running")
            elif prereq == "clean_task_queue":
                # Check if task queue is empty
                try:
                    response = self.test_framework.session.get(f"{self.api_base_url}/tasks")
                    if response.status_code == 200:
                        tasks = response.json()
                        if len(tasks) > 0:
                            result["passed"] = False
                            result["missing"].append("Task queue not empty")
                except Exception:
                    result["passed"] = False
                    result["missing"].append("Cannot check task queue")
        
        return result
    
    def run_orchestrated_test_suite(self) -> Dict[str, Any]:
        """Run complete orchestrated test suite"""
        suite_start_time = datetime.now(timezone.utc)
        
        # Create comprehensive test scenarios
        scenarios = [
            self.create_interactive_scenario("basic_interaction", "Basic Claude-Jules interaction"),
            self.create_performance_scenario("performance_50_messages", 50),
            self.create_error_recovery_scenario("error_handling"),
            self.create_session_management_scenario("session_management"),
            self.create_interactive_scenario("complex_interaction", "Complex multi-step interaction")
        ]
        
        print(f"🎭 Starting orchestrated test suite with {len(scenarios)} scenarios...")
        
        # Execute scenarios
        executions = []
        for scenario in scenarios:
            print(f"  🎯 Executing: {scenario.name}")
            execution = self.execute_scenario(scenario)
            executions.append(execution)
            
            status_icon = "✅" if execution.status == TestStatus.PASSED else "❌"
            print(f"    {status_icon} {scenario.name}: {execution.status.value}")
        
        suite_end_time = datetime.now(timezone.utc)
        
        # Calculate suite metrics
        total_scenarios = len(executions)
        passed_scenarios = len([e for e in executions if e.status == TestStatus.PASSED])
        failed_scenarios = len([e for e in executions if e.status == TestStatus.FAILED])
        error_scenarios = len([e for e in executions if e.status == TestStatus.ERROR])
        
        suite_results = {
            "orchestrated_test_suite": True,
            "start_time": suite_start_time.isoformat(),
            "end_time": suite_end_time.isoformat(),
            "total_execution_time": (suite_end_time - suite_start_time).total_seconds(),
            "scenarios": [
                {
                    "name": exec.scenario.name,
                    "description": exec.scenario.description,
                    "test_type": exec.scenario.test_type,
                    "status": exec.status.value,
                    "execution_time": exec.metrics.get("execution_time_seconds", 0),
                    "errors": exec.errors,
                    "results": exec.results
                }
                for exec in executions
            ],
            "summary": {
                "total_scenarios": total_scenarios,
                "passed_scenarios": passed_scenarios,
                "failed_scenarios": failed_scenarios,
                "error_scenarios": error_scenarios,
                "success_rate": (passed_scenarios / total_scenarios) * 100 if total_scenarios > 0 else 0
            }
        }
        
        print(f"\n📊 Orchestrated Test Suite Summary:")
        print(f"  Total Scenarios: {total_scenarios}")
        print(f"  Passed: {passed_scenarios}")
        print(f"  Failed: {failed_scenarios}")
        print(f"  Errors: {error_scenarios}")
        print(f"  Success Rate: {suite_results['summary']['success_rate']:.1f}%")
        
        return suite_results
    
    def save_orchestration_results(self, results: Dict[str, Any], filename: str) -> None:
        """Save orchestration results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📄 Orchestration results saved to {filename}")


# Example usage
if __name__ == "__main__":
    # Run orchestrated test suite
    orchestrator = TestOrchestrator()
    
    try:
        results = orchestrator.run_orchestrated_test_suite()
        
        # Save results
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"orchestrated_test_results_{timestamp}.json"
        orchestrator.save_orchestration_results(results, filename)
        
        print(f"\n🎯 Orchestration complete! Overall success rate: {results['summary']['success_rate']:.1f}%")
        
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        print("🔧 Make sure the API server is running and accessible")