#!/usr/bin/env python3
"""
Test script for the input ticket handling functionality
Run this to verify that ticket input processing works correctly
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models import create_initial_state, validate_ticket_input
from input_handler import handle_input_ticket, extract_ticket_metadata


def test_ticket_validation():
    """Test the ticket validation function"""
    print("🧪 Testing Ticket Validation")
    print("=" * 40)
    
    test_cases = [
        ("Valid ticket", "This is a detailed description of my problem with the login system", True),
        ("", "Good description", False),  # Empty subject
        ("Good subject", "", False),  # Empty description
        ("Hi", "Short desc", False),  # Too short
        ("Good subject", "Good description that meets minimum requirements", True),
    ]
    
    for subject, description, expected_valid in test_cases:
        is_valid, error_msg = validate_ticket_input(subject, description)
        status = "✅ PASS" if is_valid == expected_valid else "❌ FAIL"
        print(f"{status} | Valid: {is_valid} | Subject: '{subject[:20]}...' | Error: {error_msg}")
    
    print()


def test_initial_state_creation():
    """Test creating initial state from ticket input"""
    print("🧪 Testing Initial State Creation")
    print("=" * 40)
    
    try:
        state = create_initial_state(
            subject="Test login issue",
            description="I cannot log into my account and need help urgently",
            priority="high"
        )
        
        print("✅ Initial state created successfully")
        print(f"Ticket ID: {state['ticket'].ticket_id}")
        print(f"Subject: {state['ticket'].subject}")
        print(f"Priority: {state['ticket'].priority}")
        print(f"Processing logs: {len(state['processing_log'])} entries")
        
        for log in state['processing_log']:
            print(f"  - {log}")
            
    except Exception as e:
        print(f"❌ Error creating initial state: {e}")
    
    print()


def test_input_handler_node():
    """Test the input handler node processing"""
    print("🧪 Testing Input Handler Node")
    print("=" * 40)
    
    # Create test ticket
    state = create_initial_state(
        subject="Login problems on mobile app",
        description="The app keeps saying 'invalid credentials' but I know my password is correct. This is happening on my iPhone."
    )
    
    print(f"Before processing:")
    print(f"  Original subject: '{state['ticket'].subject}'")
    print(f"  Processing logs: {len(state['processing_log'])}")
    
    # Process through input handler
    processed_state = handle_input_ticket(state)
    
    print(f"After processing:")
    print(f"  Processed subject: '{processed_state['ticket'].subject}'")
    print(f"  Processing logs: {len(processed_state['processing_log'])}")
    
    print("Processing log:")
    for log in processed_state['processing_log']:
        print(f"  - {log}")
    
    # Extract metadata
    metadata = extract_ticket_metadata(processed_state['ticket'])
    print(f"Extracted metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    print()


def test_multiple_ticket_types():
    """Test different types of tickets"""
    print("🧪 Testing Multiple Ticket Types")
    print("=" * 50)
    
    tickets = [
        {
            "subject": "Billing question about my subscription",
            "description": "I was charged twice for my monthly subscription. Can you help me get a refund for the duplicate charge?",
            "type": "Billing"
        },
        {
            "subject": "Cannot access dashboard - technical issue",
            "description": "When I try to access my dashboard, I get a 500 error. This started happening yesterday after the maintenance.",
            "type": "Technical"
        },
        {
            "subject": "Security alert - suspicious login attempt",
            "description": "I received an email about a login attempt from an unknown location. I want to secure my account immediately.",
            "type": "Security"
        },
        {
            "subject": "General question about features",
            "description": "I'm wondering if you have any plans to add dark mode to the application. It would be really helpful for night usage.",
            "type": "General"
        }
    ]
    
    for i, ticket_data in enumerate(tickets, 1):
        print(f"--- Ticket {i}: {ticket_data['type']} ---")
        
        try:
            # Create and process
            state = create_initial_state(
                subject=ticket_data['subject'],
                description=ticket_data['description']
            )
            
            processed_state = handle_input_ticket(state)
            
            # Show key information
            ticket = processed_state['ticket']
            metadata = extract_ticket_metadata(ticket)
            
            print(f"✅ Processed: {ticket.ticket_id}")
            print(f"Subject: {ticket.subject}")
            print(f"Word counts: Subject={metadata['word_count_subject']}, Description={metadata['word_count_description']}")
            print(f"Keywords found:")
            print(f"  - Urgency: {metadata['urgency_keywords']}")
            print(f"  - Technical: {metadata['technical_keywords']}")
            print(f"  - Billing: {metadata['billing_keywords']}")
            
        except Exception as e:
            print(f"❌ Error processing ticket: {e}")
        
        print()


def main():
    """Run all tests"""
    print("🎯 Support Ticket Input Handler - Test Suite")
    print("=" * 60)
    print()
    
    test_ticket_validation()
    test_initial_state_creation()
    test_input_handler_node()
    test_multiple_ticket_types()
    
    print("🏁 All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()