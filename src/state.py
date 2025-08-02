# src/state.py
from typing_extensions import TypedDict
from typing import Optional, List, Dict

class SupportTicketState(TypedDict):
    # Input fields
    subject: str
    description: str
    
    # Classification output
    classification: Optional[str]
    
    # RAG fields - ADD THESE
    retrieved_context: Optional[List[Dict]]
    formatted_context: Optional[str]
    retrieval_attempt: Optional[int]
    
    # Draft and review fields
    draft_response: Optional[str]
    review_passed: Optional[bool]
    reviewer_feedback: Optional[str]
    draft_attempt: Optional[int]
    max_attempts_reached: Optional[bool]
    
    # Escalation fields
    escalated: Optional[bool]
    max_attempts_reached: Optional[bool]