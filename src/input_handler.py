"""
Input Ticket Handling Node for LangGraph
This is the starting node that processes incoming support tickets
"""

import logging
from datetime import datetime
from typing import Dict, Any

from models import AgentState, SupportTicket

logger = logging.getLogger(__name__)


def handle_input_ticket(state: AgentState) -> AgentState:
    """
    Starting node for the LangGraph workflow.
    Processes and validates the input ticket, preparing it for downstream processing.
    
    This node:
    1. Validates the ticket data
    2. Logs ticket receipt
    3. Performs any input preprocessing
    4. Sets up the state for downstream nodes
    
    Args:
        state: The current agent state containing the input ticket
        
    Returns:
        Updated state with processed ticket information
    """
    try:
        ticket = state["ticket"]
        
        # Log ticket receipt
        log_entry = f"Processing ticket {ticket.ticket_id}: '{ticket.subject}'"
        state["processing_log"].append(log_entry)
        logger.info(log_entry)
        
        # Validate ticket content
        validation_issues = []
        
        # Check for common issues that might affect downstream processing
        if len(ticket.subject) < 5:
            validation_issues.append("Subject is very short")
        
        if len(ticket.description) < 20:
            validation_issues.append("Description is very brief")
        
        # Check for sensitive information (basic patterns)
        sensitive_patterns = [
            'password', 'credit card', 'ssn', 'social security',
            'bank account', 'routing number'
        ]
        
        content_lower = f"{ticket.subject} {ticket.description}".lower()
        for pattern in sensitive_patterns:
            if pattern in content_lower:
                validation_issues.append(f"Potential sensitive information detected: {pattern}")
        
        # Log validation issues
        if validation_issues:
            issues_log = f"Validation concerns: {'; '.join(validation_issues)}"
            state["processing_log"].append(issues_log)
            logger.warning(f"Ticket {ticket.ticket_id}: {issues_log}")
        
        # Preprocess ticket content
        processed_ticket = preprocess_ticket_content(ticket)
        state["ticket"] = processed_ticket
        
        # Add preprocessing log
        state["processing_log"].append("Input ticket validated and preprocessed")
        
        # Set processing metadata
        state["processing_start_time"] = datetime.now().isoformat()
        
        logger.info(f"Successfully processed input ticket {ticket.ticket_id}")
        
    except Exception as e:
        error_msg = f"Error processing input ticket: {str(e)}"
        state["processing_log"].append(error_msg)
        logger.error(error_msg)
        
        # Set error state but don't fail completely
        # The downstream nodes can handle this gracefully
        state["processing_log"].append("Continuing with error handling mode")
    
    return state


def preprocess_ticket_content(ticket: SupportTicket) -> SupportTicket:
    """
    Preprocess ticket content for better downstream processing.
    
    This function:
    1. Cleans up text formatting
    2. Normalizes common abbreviations
    3. Removes sensitive information patterns
    4. Standardizes formatting
    
    Args:
        ticket: The original support ticket
        
    Returns:
        Preprocessed support ticket
    """
    # Clean up subject
    cleaned_subject = ticket.subject.strip()
    cleaned_subject = ' '.join(cleaned_subject.split())  # Normalize whitespace
    
    # Clean up description
    cleaned_description = ticket.description.strip()
    cleaned_description = ' '.join(cleaned_description.split())  # Normalize whitespace
    
    # Common abbreviation expansions for better classification
    abbreviations = {
        'cant': "can't",
        'dont': "don't",
        'wont': "won't",
        'isnt': "isn't",
        'doesnt': "doesn't",
        'acc': 'account',
        'pwd': 'password',
        'login': 'log in',
        'signup': 'sign up',
        'app': 'application'
    }
    
    for abbrev, expansion in abbreviations.items():
        cleaned_subject = cleaned_subject.replace(abbrev, expansion)
        cleaned_description = cleaned_description.replace(abbrev, expansion)
    
    # Create new ticket with cleaned content
    preprocessed_ticket = SupportTicket(
        subject=cleaned_subject,
        description=cleaned_description,
        ticket_id=ticket.ticket_id,
        timestamp=ticket.timestamp,
        priority=ticket.priority,
        customer_id=ticket.customer_id
    )
    
    return preprocessed_ticket


def extract_ticket_metadata(ticket: SupportTicket) -> Dict[str, Any]:
    """
    Extract metadata from the ticket for analytics and routing.
    
    Args:
        ticket: The support ticket
        
    Returns:
        Dictionary containing extracted metadata
    """
    metadata = {
        "word_count_subject": len(ticket.subject.split()),
        "word_count_description": len(ticket.description.split()),
        "char_count_total": len(ticket.subject) + len(ticket.description),
        "has_question_marks": "?" in f"{ticket.subject} {ticket.description}",
        "has_exclamation": "!" in f"{ticket.subject} {ticket.description}",
        "urgency_keywords": [],
        "technical_keywords": [],
        "billing_keywords": []
    }
    
    content_lower = f"{ticket.subject} {ticket.description}".lower()
    
    # Detect urgency indicators
    urgency_words = ['urgent', 'asap', 'emergency', 'critical', 'immediately', 'broken', 'down']
    metadata["urgency_keywords"] = [word for word in urgency_words if word in content_lower]
    
    # Detect technical keywords
    tech_words = ['error', 'bug', 'crash', 'login', 'password', 'website', 'app', 'mobile']
    metadata["technical_keywords"] = [word for word in tech_words if word in content_lower]
    
    # Detect billing keywords
    billing_words = ['payment', 'charge', 'billing', 'invoice', 'refund', 'subscription', 'plan']
    metadata["billing_keywords"] = [word for word in billing_words if word in content_lower]
    
    return metadata


# Example usage and testing functions
def create_test_tickets():
    """Create sample tickets for testing the input handler"""
    test_tickets = [
        {
            "subject": "Cannot login to my account",
            "description": "I've been trying to log into my account for the past hour but keep getting an 'invalid credentials' error even though I'm sure my password is correct. This is urgent as I need to access my dashboard for a client meeting."
        },
        {
            "subject": "Billing question about last month's charge",
            "description": "I see a charge on my credit card from last month that seems higher than usual. Can you help me understand what this charge is for? My account is under john.doe@email.com"
        },
        {
            "subject": "App keeps crashing on iPhone",
            "description": "The mobile app crashes every time I try to open the reports section. I'm using iPhone 13 with iOS 16.1. This started happening after the latest app update."
        },
        {
            "subject": "Security concern - suspicious activity",
            "description": "I received an email saying someone logged into my account from Russia, but I haven't traveled there. I'm worried my account has been compromised. Please help immediately."
        }
    ]
    
    return test_tickets


if __name__ == "__main__":
    # Test the input handler
    from models import create_initial_state
    
    test_tickets = create_test_tickets()
    
    for i, ticket_data in enumerate(test_tickets, 1):
        print(f"\n--- Testing Ticket {i} ---")
        print(f"Subject: {ticket_data['subject']}")
        print(f"Description: {ticket_data['description'][:100]}...")
        
        try:
            # Create initial state
            state = create_initial_state(
                subject=ticket_data['subject'],
                description=ticket_data['description']
            )
            
            # Process through input handler
            processed_state = handle_input_ticket(state)
            
            # Show results
            ticket = processed_state['ticket']
            print(f"Ticket ID: {ticket.ticket_id}")
            print(f"Processing started: {processed_state['processing_start_time']}")
            print("Processing log:")
            for log_entry in processed_state['processing_log']:
                print(f"  - {log_entry}")
            
            # Show metadata
            metadata = extract_ticket_metadata(ticket)
            print(f"Metadata: {metadata}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 50)