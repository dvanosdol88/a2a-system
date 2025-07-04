"""
A2A Message Types and Schemas
Rich messaging system for Agent-to-Agent communication
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List, Union
from enum import Enum
import json
import uuid
from datetime import datetime, timezone


class MessageType(Enum):
    """Message type enumeration"""
    SIMPLE_TASK = "simple_task"
    COMPLEX_TASK = "complex_task"
    BATCH_TASK = "batch_task"
    PRIORITY_TASK = "priority_task"
    SESSION_START = "session_start"
    SESSION_UPDATE = "session_update"
    SESSION_END = "session_end"
    HEALTH_CHECK = "health_check"
    ERROR_REPORT = "error_report"
    STATUS_UPDATE = "status_update"
    RESULT_REPORT = "result_report"


class Priority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY_NEEDED = "retry_needed"


@dataclass
class MessageMetadata:
    """Standard metadata for all messages"""
    message_id: str
    timestamp: str
    sender: str
    recipient: str
    message_type: MessageType
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 30
    
    def __post_init__(self):
        if isinstance(self.message_type, str):
            self.message_type = MessageType(self.message_type)


@dataclass
class SimpleTask:
    """Basic task message"""
    task_description: str
    expected_duration: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class ComplexTask:
    """Multi-step task with dependencies"""
    task_description: str
    steps: List[Dict[str, Any]]
    dependencies: List[str]
    expected_duration: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class BatchTask:
    """Collection of related tasks"""
    batch_name: str
    tasks: List[Union[SimpleTask, ComplexTask]]
    execution_mode: str = "sequential"  # sequential, parallel, priority
    context: Optional[Dict[str, Any]] = None


@dataclass
class PriorityTask:
    """High-priority task with SLA"""
    task_description: str
    priority: Priority
    deadline: Optional[str] = None
    escalation_contact: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class SessionInfo:
    """Session management data"""
    session_id: str
    session_name: str
    participants: List[str]
    session_data: Dict[str, Any]
    created_at: str
    expires_at: Optional[str] = None


@dataclass
class ErrorInfo:
    """Error reporting structure"""
    error_code: str
    error_message: str
    error_details: Dict[str, Any]
    stack_trace: Optional[str] = None
    recovery_suggestions: List[str] = None


@dataclass
class ResultInfo:
    """Task result reporting"""
    task_id: str
    status: TaskStatus
    result_data: Dict[str, Any]
    execution_time: Optional[float] = None
    error_info: Optional[ErrorInfo] = None


@dataclass
class A2AMessage:
    """Complete A2A message structure"""
    metadata: MessageMetadata
    payload: Union[SimpleTask, ComplexTask, BatchTask, PriorityTask, SessionInfo, ErrorInfo, ResultInfo, Dict[str, Any]]
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(asdict(self), default=str, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'A2AMessage':
        """Create message from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Create message from dictionary"""
        metadata = MessageMetadata(**data['metadata'])
        payload = data['payload']
        return cls(metadata=metadata, payload=payload)


class MessageBuilder:
    """Builder pattern for creating A2A messages"""
    
    def __init__(self, sender: str, recipient: str):
        self.sender = sender
        self.recipient = recipient
    
    def create_simple_task(self, description: str, session_id: Optional[str] = None) -> A2AMessage:
        """Create a simple task message"""
        metadata = MessageMetadata(
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            sender=self.sender,
            recipient=self.recipient,
            message_type=MessageType.SIMPLE_TASK,
            session_id=session_id
        )
        
        payload = SimpleTask(task_description=description)
        return A2AMessage(metadata=metadata, payload=payload)
    
    def create_complex_task(self, description: str, steps: List[Dict[str, Any]], 
                           dependencies: List[str] = None, session_id: Optional[str] = None) -> A2AMessage:
        """Create a complex task message"""
        metadata = MessageMetadata(
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            sender=self.sender,
            recipient=self.recipient,
            message_type=MessageType.COMPLEX_TASK,
            session_id=session_id
        )
        
        payload = ComplexTask(
            task_description=description,
            steps=steps,
            dependencies=dependencies or []
        )
        return A2AMessage(metadata=metadata, payload=payload)
    
    def create_session_start(self, session_name: str, participants: List[str], 
                           session_data: Dict[str, Any] = None) -> A2AMessage:
        """Create session start message"""
        session_id = str(uuid.uuid4())
        metadata = MessageMetadata(
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            sender=self.sender,
            recipient=self.recipient,
            message_type=MessageType.SESSION_START,
            session_id=session_id
        )
        
        payload = SessionInfo(
            session_id=session_id,
            session_name=session_name,
            participants=participants,
            session_data=session_data or {},
            created_at=datetime.now(timezone.utc).isoformat()
        )
        return A2AMessage(metadata=metadata, payload=payload)
    
    def create_error_report(self, error_code: str, error_message: str, 
                          error_details: Dict[str, Any], session_id: Optional[str] = None) -> A2AMessage:
        """Create error report message"""
        metadata = MessageMetadata(
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            sender=self.sender,
            recipient=self.recipient,
            message_type=MessageType.ERROR_REPORT,
            session_id=session_id
        )
        
        payload = ErrorInfo(
            error_code=error_code,
            error_message=error_message,
            error_details=error_details
        )
        return A2AMessage(metadata=metadata, payload=payload)
    
    def create_result_report(self, task_id: str, status: TaskStatus, 
                           result_data: Dict[str, Any], session_id: Optional[str] = None) -> A2AMessage:
        """Create result report message"""
        metadata = MessageMetadata(
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            sender=self.sender,
            recipient=self.recipient,
            message_type=MessageType.RESULT_REPORT,
            session_id=session_id
        )
        
        payload = ResultInfo(
            task_id=task_id,
            status=status,
            result_data=result_data
        )
        return A2AMessage(metadata=metadata, payload=payload)


# Convenience functions for common operations
def create_claude_to_jules_builder() -> MessageBuilder:
    """Create message builder for Claude -> Jules communication"""
    return MessageBuilder(sender="claude", recipient="jules")


def create_jules_to_claude_builder() -> MessageBuilder:
    """Create message builder for Jules -> Claude communication"""
    return MessageBuilder(sender="jules", recipient="claude")


def validate_message_schema(message_data: Dict[str, Any]) -> bool:
    """Validate message against A2A schema"""
    required_fields = ['metadata', 'payload']
    metadata_fields = ['message_id', 'timestamp', 'sender', 'recipient', 'message_type']
    
    try:
        # Check top-level structure
        for field in required_fields:
            if field not in message_data:
                return False
        
        # Check metadata structure
        metadata = message_data['metadata']
        for field in metadata_fields:
            if field not in metadata:
                return False
        
        # Validate message type
        MessageType(metadata['message_type'])
        
        return True
    except (KeyError, ValueError, TypeError):
        return False


# Example usage and testing
if __name__ == "__main__":
    # Example: Create a simple task message
    builder = create_claude_to_jules_builder()
    
    simple_msg = builder.create_simple_task(
        description="Test the API health endpoint",
        session_id="test-session-001"
    )
    
    print("Simple Task Message:")
    print(simple_msg.to_json())
    
    # Example: Create a complex task message
    complex_msg = builder.create_complex_task(
        description="Set up comprehensive testing framework",
        steps=[
            {"step": 1, "action": "Create test data generator"},
            {"step": 2, "action": "Build test scenarios"},
            {"step": 3, "action": "Execute interactive tests"}
        ],
        dependencies=["message_types_complete"],
        session_id="test-session-001"
    )
    
    print("\nComplex Task Message:")
    print(complex_msg.to_json())