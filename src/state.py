# src/state.py
from typing_extensions import TypedDict
from typing import Optional, List, Dict

class SupportTicketState(TypedDict):
   
    subject: str
    description: str
    
 
    classification: Optional[str]
    

    retrieved_context: Optional[List[Dict]]
    formatted_context: Optional[str]
    retrieval_attempt: Optional[int]
    
   
    draft_response: Optional[str]
    review_passed: Optional[bool]
    reviewer_feedback: Optional[str]
    draft_attempt: Optional[int]
   
    
   
    escalated: Optional[bool]
    max_attempts_reached: Optional[bool]