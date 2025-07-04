"""
A2A Test Data Generator
Generates realistic test scenarios for comprehensive A2A system testing
"""

import random
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
import uuid

from shared.message_types import (
    MessageBuilder, MessageType, Priority, TaskStatus, A2AMessage,
    SimpleTask, ComplexTask, BatchTask, PriorityTask
)


class TestDataGenerator:
    """Generates comprehensive test data for A2A system testing"""
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
        
        self.task_templates = {
            "simple": [
                "Check system health status",
                "Verify API endpoint functionality",
                "Run basic connectivity test",
                "Validate configuration settings",
                "Monitor resource usage",
                "Test file system access",
                "Verify network connectivity",
                "Check database connection",
                "Validate authentication flow",
                "Test error handling mechanism"
            ],
            "complex": [
                {
                    "description": "Deploy new application version",
                    "steps": [
                        {"step": 1, "action": "Backup current version"},
                        {"step": 2, "action": "Run pre-deployment tests"},
                        {"step": 3, "action": "Deploy to staging environment"},
                        {"step": 4, "action": "Execute integration tests"},
                        {"step": 5, "action": "Deploy to production"},
                        {"step": 6, "action": "Verify deployment success"}
                    ]
                },
                {
                    "description": "Comprehensive system audit",
                    "steps": [
                        {"step": 1, "action": "Collect system metrics"},
                        {"step": 2, "action": "Analyze performance data"},
                        {"step": 3, "action": "Identify bottlenecks"},
                        {"step": 4, "action": "Generate recommendations"},
                        {"step": 5, "action": "Create improvement plan"}
                    ]
                },
                {
                    "description": "Security vulnerability assessment",
                    "steps": [
                        {"step": 1, "action": "Scan for known vulnerabilities"},
                        {"step": 2, "action": "Test authentication mechanisms"},
                        {"step": 3, "action": "Validate access controls"},
                        {"step": 4, "action": "Check encryption implementation"},
                        {"step": 5, "action": "Generate security report"}
                    ]
                }
            ]
        }
        
        self.error_scenarios = [
            {"code": "TIMEOUT", "message": "Operation timed out", "recoverable": True},
            {"code": "NETWORK_ERROR", "message": "Network connection failed", "recoverable": True},
            {"code": "AUTH_FAILED", "message": "Authentication failed", "recoverable": False},
            {"code": "RESOURCE_EXHAUSTED", "message": "System resources exhausted", "recoverable": True},
            {"code": "DATA_CORRUPTION", "message": "Data integrity check failed", "recoverable": False},
            {"code": "SERVICE_UNAVAILABLE", "message": "Required service unavailable", "recoverable": True}
        ]
    
    def generate_simple_tasks(self, count: int = 10) -> List[A2AMessage]:
        """Generate simple task messages"""
        builder = MessageBuilder(sender="test_generator", recipient="jules")
        tasks = []
        
        for _ in range(count):
            task_desc = random.choice(self.task_templates["simple"])
            task = builder.create_simple_task(description=task_desc)
            tasks.append(task)
        
        return tasks
    
    def generate_complex_tasks(self, count: int = 5) -> List[A2AMessage]:
        """Generate complex task messages"""
        builder = MessageBuilder(sender="test_generator", recipient="jules")
        tasks = []
        
        for _ in range(count):
            template = random.choice(self.task_templates["complex"])
            task = builder.create_complex_task(
                description=template["description"],
                steps=template["steps"],
                dependencies=self._generate_dependencies()
            )
            tasks.append(task)
        
        return tasks
    
    def generate_priority_tasks(self, count: int = 3) -> List[A2AMessage]:
        """Generate priority task messages"""
        builder = MessageBuilder(sender="test_generator", recipient="jules")
        tasks = []
        
        for _ in range(count):
            task_desc = f"URGENT: {random.choice(self.task_templates['simple'])}"
            deadline = (datetime.now(timezone.utc) + timedelta(minutes=random.randint(5, 30))).isoformat()
            
            # Create priority task using message builder
            metadata = builder.create_simple_task(task_desc).metadata
            metadata.message_type = MessageType.PRIORITY_TASK
            
            payload = PriorityTask(
                task_description=task_desc,
                priority=Priority.URGENT,
                deadline=deadline,
                escalation_contact="system_admin"
            )
            
            task = A2AMessage(metadata=metadata, payload=payload)
            tasks.append(task)
        
        return tasks
    
    def generate_batch_tasks(self, count: int = 2) -> List[A2AMessage]:
        """Generate batch task messages"""
        builder = MessageBuilder(sender="test_generator", recipient="jules")
        batches = []
        
        for i in range(count):
            # Create subtasks
            subtasks = []
            for j in range(random.randint(3, 7)):
                subtask = SimpleTask(
                    task_description=f"Batch {i+1} - Task {j+1}: {random.choice(self.task_templates['simple'])}"
                )
                subtasks.append(subtask)
            
            # Create batch task
            metadata = builder.create_simple_task("batch_placeholder").metadata
            metadata.message_type = MessageType.BATCH_TASK
            
            payload = BatchTask(
                batch_name=f"Test Batch {i+1}",
                tasks=subtasks,
                execution_mode=random.choice(["sequential", "parallel"])
            )
            
            batch = A2AMessage(metadata=metadata, payload=payload)
            batches.append(batch)
        
        return batches
    
    def generate_session_scenarios(self, count: int = 3) -> List[List[A2AMessage]]:
        """Generate complete session scenarios"""
        scenarios = []
        
        for i in range(count):
            builder = MessageBuilder(sender="test_generator", recipient="jules")
            scenario = []
            
            # Session start
            session_start = builder.create_session_start(
                session_name=f"Test Session {i+1}",
                participants=["claude", "jules", "test_generator"],
                session_data={
                    "test_type": "comprehensive",
                    "expected_tasks": random.randint(5, 15),
                    "timeout_minutes": random.randint(10, 60)
                }
            )
            scenario.append(session_start)
            
            # Add various tasks
            scenario.extend(self.generate_simple_tasks(random.randint(2, 5)))
            scenario.extend(self.generate_complex_tasks(random.randint(1, 2)))
            
            # Add some errors
            if random.random() < 0.3:  # 30% chance of error
                error_scenario = random.choice(self.error_scenarios)
                error_msg = builder.create_error_report(
                    error_code=error_scenario["code"],
                    error_message=error_scenario["message"],
                    error_details={
                        "recoverable": error_scenario["recoverable"],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "context": "test_scenario"
                    }
                )
                scenario.append(error_msg)
            
            scenarios.append(scenario)
        
        return scenarios
    
    def generate_error_scenarios(self, count: int = 10) -> List[A2AMessage]:
        """Generate error scenario messages"""
        builder = MessageBuilder(sender="test_generator", recipient="jules")
        errors = []
        
        for _ in range(count):
            error_data = random.choice(self.error_scenarios)
            error_msg = builder.create_error_report(
                error_code=error_data["code"],
                error_message=error_data["message"],
                error_details={
                    "recoverable": error_data["recoverable"],
                    "retry_count": random.randint(0, 3),
                    "error_context": self._generate_error_context(),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            errors.append(error_msg)
        
        return errors
    
    def generate_performance_test_data(self, message_count: int = 100) -> List[A2AMessage]:
        """Generate data for performance testing"""
        messages = []
        
        # Mix of different message types
        messages.extend(self.generate_simple_tasks(int(message_count * 0.5)))
        messages.extend(self.generate_complex_tasks(int(message_count * 0.3)))
        messages.extend(self.generate_priority_tasks(int(message_count * 0.1)))
        messages.extend(self.generate_batch_tasks(int(message_count * 0.1)))
        
        # Randomize order
        random.shuffle(messages)
        
        return messages
    
    def generate_stress_test_data(self, concurrent_sessions: int = 5, 
                                 messages_per_session: int = 50) -> Dict[str, List[A2AMessage]]:
        """Generate data for stress testing"""
        stress_data = {}
        
        for i in range(concurrent_sessions):
            session_name = f"stress_session_{i+1}"
            messages = self.generate_performance_test_data(messages_per_session)
            
            # Add session context to all messages
            for msg in messages:
                msg.metadata.session_id = session_name
                msg.metadata.correlation_id = f"stress_test_{i+1}"
            
            stress_data[session_name] = messages
        
        return stress_data
    
    def generate_edge_case_data(self) -> List[A2AMessage]:
        """Generate edge case test data"""
        builder = MessageBuilder(sender="test_generator", recipient="jules")
        edge_cases = []
        
        # Very long task description
        long_desc = "A" * 5000  # 5KB description
        edge_cases.append(builder.create_simple_task(long_desc))
        
        # Task with special characters
        special_chars = "Task with special chars: !@#$%^&*()_+{}|:<>?[];',./"
        edge_cases.append(builder.create_simple_task(special_chars))
        
        # Task with unicode
        unicode_desc = "Task with unicode: 你好世界 🌍 عالم مرحبا"
        edge_cases.append(builder.create_simple_task(unicode_desc))
        
        # Complex task with many steps
        many_steps = [{"step": i, "action": f"Step {i} action"} for i in range(1, 101)]
        edge_cases.append(builder.create_complex_task(
            "Task with 100 steps",
            steps=many_steps
        ))
        
        return edge_cases
    
    def _generate_dependencies(self) -> List[str]:
        """Generate random dependencies"""
        deps = ["system_check", "auth_validation", "resource_allocation", "config_load"]
        return random.sample(deps, random.randint(0, 2))
    
    def _generate_error_context(self) -> Dict[str, Any]:
        """Generate error context data"""
        return {
            "component": random.choice(["api", "database", "filesystem", "network"]),
            "severity": random.choice(["low", "medium", "high", "critical"]),
            "user_impact": random.choice(["none", "minimal", "moderate", "severe"]),
            "system_load": random.uniform(0.1, 1.0)
        }
    
    def save_test_data(self, filename: str, data: Any) -> None:
        """Save test data to JSON file"""
        with open(filename, 'w') as f:
            if isinstance(data, list) and len(data) > 0 and hasattr(data[0], 'to_json'):
                # Handle A2AMessage objects
                json_data = [json.loads(msg.to_json()) for msg in data]
                json.dump(json_data, f, indent=2)
            else:
                json.dump(data, f, indent=2, default=str)
    
    def generate_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Generate complete test suite"""
        return {
            "simple_tasks": self.generate_simple_tasks(20),
            "complex_tasks": self.generate_complex_tasks(10),
            "priority_tasks": self.generate_priority_tasks(5),
            "batch_tasks": self.generate_batch_tasks(3),
            "session_scenarios": self.generate_session_scenarios(5),
            "error_scenarios": self.generate_error_scenarios(15),
            "performance_data": self.generate_performance_test_data(200),
            "stress_data": self.generate_stress_test_data(3, 30),
            "edge_cases": self.generate_edge_case_data()
        }


# Example usage and testing
if __name__ == "__main__":
    generator = TestDataGenerator(seed=42)  # Fixed seed for reproducible tests
    
    # Generate sample data
    simple_tasks = generator.generate_simple_tasks(3)
    print("Generated Simple Tasks:")
    for task in simple_tasks:
        print(f"- {task.payload.task_description}")
    
    # Generate and save comprehensive test suite
    test_suite = generator.generate_comprehensive_test_suite()
    
    print(f"\nGenerated comprehensive test suite:")
    print(f"- Simple tasks: {len(test_suite['simple_tasks'])}")
    print(f"- Complex tasks: {len(test_suite['complex_tasks'])}")
    print(f"- Priority tasks: {len(test_suite['priority_tasks'])}")
    print(f"- Batch tasks: {len(test_suite['batch_tasks'])}")
    print(f"- Session scenarios: {len(test_suite['session_scenarios'])}")
    print(f"- Error scenarios: {len(test_suite['error_scenarios'])}")
    print(f"- Performance test messages: {len(test_suite['performance_data'])}")
    print(f"- Stress test sessions: {len(test_suite['stress_data'])}")
    print(f"- Edge cases: {len(test_suite['edge_cases'])}")
    
    # Save test data
    generator.save_test_data("test_data_sample.json", simple_tasks)