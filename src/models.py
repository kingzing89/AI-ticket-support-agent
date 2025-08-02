"""
Data models for the Support Ticket Resolution Agent
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, TypedDict
from enum import Enum


class TicketCategory(Enum):
    """Predefined ticket categories"""
    BILLING = "billing"
    TECHNICAL = "technical"
    SECURITY = "security"
    GENERAL = "general"


@dataclass
class SupportTicket:
    """
    Represents an incoming support ticket - this is our input data structure.
    This is the starting point of our graph workflow.
    """
    subject: str
    description: str
    ticket_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    priority: str = "normal"  # low, normal, high, urgent
    customer_id: Optional[str] = None
    
    def __post_init__(self):
        """Generate ticket ID if not provided"""
        if self.ticket_id is None:
            self.ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "ticket_id": self.ticket_id,
            "subject": self.subject,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "customer_id": self.customer_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SupportTicket':
        """Create SupportTicket from dictionary"""
        timestamp = datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
        return cls(
            subject=data['subject'],
            description=data['description'],
            ticket_id=data.get('ticket_id'),
            timestamp=timestamp,
            priority=data.get('priority', 'normal'),
            customer_id=data.get('customer_id')
        )


@dataclass
class ReviewResult:
    """Result from the draft reviewer"""
    approved: bool
    feedback: str
    score: float = 0.0
    review_timestamp: datetime = field(default_factory=datetime.now)


class AgentState(TypedDict):
    """
    State maintained throughout the support agent workflow.
    This flows through all nodes in our LangGraph.
    """
    # Input data - this is where our ticket enters the system
    ticket: SupportTicket
    
    # Processing state
    classification: Optional[str]
    retrieved_context: List[str]
    current_draft: Optional[str]
    review_result: Optional[ReviewResult]
    
    # Control flow
    retry_count: int
    reviewer_feedback: List[str]
    escalated: bool
    
    # Final output
    final_response: Optional[str]
    processing_log: List[str]
    
    # Metadata
    processing_start_time: Optional[str]
    processing_end_time: Optional[str]


def validate_ticket_input(subject: str, description: str) -> tuple[bool, str]:
    """
    Validate input ticket data before processing.
    Returns (is_valid, error_message)
    """
    if not subject or not subject.strip():
        return False, "Subject cannot be empty"
    
    if not description or not description.strip():
        return False, "Description cannot be empty"
    
    if len(subject.strip()) < 3:
        return False, "Subject must be at least 3 characters long"
    
    if len(description.strip()) < 10:
        return False, "Description must be at least 10 characters long"
    
    if len(subject) > 200:
        return False, "Subject must be less than 200 characters"
    
    if len(description) > 5000:
        return False, "Description must be less than 5000 characters"
    
    return True, ""


def create_initial_state(subject: str, description: str, **kwargs) -> AgentState:
    """
    Create the initial state for the LangGraph workflow.
    This is the entry point that handles input ticket processing.
    """
    # Validate input
    is_valid, error_message = validate_ticket_input(subject, description)
    if not is_valid:
        raise ValueError(f"Invalid ticket input: {error_message}")
    
    # Create the support ticket
    ticket = SupportTicket(
        subject=subject.strip(),
        description=description.strip(),
        priority=kwargs.get('priority', 'normal'),
        customer_id=kwargs.get('customer_id')
    )
    
    # Create initial state
    initial_state: AgentState = {
        "ticket": ticket,
        "classification": None,
        "retrieved_context": [],
        "current_draft": None,
        "review_result": None,
        "retry_count": 0,
        "reviewer_feedback": [],
        "escalated": False,
        "final_response": None,
        "processing_log": [
            f"Ticket {ticket.ticket_id} created at {ticket.timestamp.isoformat()}",
            f"Subject: {ticket.subject}",
            f"Priority: {ticket.priority}"
        ],
        "processing_start_time": datetime.now().isoformat(),
        "processing_end_time": None
    }
    
    return initial_state