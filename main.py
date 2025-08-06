#!/usr/bin/env python3
"""
Main application entry point for the Support Ticket Resolution Agent
Run this file to test the complete workflow
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import create_support_graph
from src.state import SupportTicketState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('support_agent.log')
    ]
)

logger = logging.getLogger(__name__)


def create_test_tickets():
    """Create sample tickets for testing"""
    return [
        {
            "subject": "Cannot login to my account",
            "description": "I've been trying to log into my account for the past hour but keep getting an 'invalid credentials' error even though I'm sure my password is correct. This is urgent as I need to access my dashboard for a client meeting."
        },
        {
            "subject": "Double charged this month",
            "description": "I was charged $29.99 twice for my monthly subscription on my credit card. Can you please help me get a refund for the duplicate charge? My account email is john@example.com"
        },
        {
            "subject": "Mobile app keeps crashing",
            "description": "The mobile app crashes every time I try to open the reports section. I'm using iPhone 13 with iOS 16.1. This started happening after the latest app update yesterday."
        },
        {
            "subject": "How to export my data?",
            "description": "I need to export all my data for backup purposes. Is there a way to do bulk data export? I couldn't find this option in the settings menu."
        },
        {
            "subject": "Suspicious login activity",
            "description": "I received an email saying someone logged into my account from Russia, but I haven't traveled there. I'm worried my account has been compromised. Please help immediately!"
        }
    ]


def create_initial_state(subject: str, description: str) -> SupportTicketState:

    return {
        "subject": subject,
        "description": description,
        "classification": None,
        "retrieved_context": None,
        "formatted_context": None,
        "retrieval_attempt": 1,  # <-- Initialize to 1
        "draft_response": None,
        "review_passed": None,
        "reviewer_feedback": None,
        "draft_attempt": 1,      # <-- Initialize to 1
        "max_attempts_reached": None,
        "escalated": None,
        "processing_log": [],
    }


def print_state_summary(state: SupportTicketState, step: str):
  
    print(f"\n{'='*60}")
    print(f"STEP: {step}")
    print(f"{'='*60}")
    
    if step == "INPUT":
        print(f"Subject: {state['subject']}")
        print(f"Description: {state['description'][:100]}...")
    
    elif step == "CLASSIFICATION":
        print(f"Classification: {state.get('classification', 'Not set')}")
    
    elif step == "RAG_RETRIEVAL":
        context = state.get('retrieved_context', [])
        print(f"Retrieved {len(context)} documents")
        attempt = state.get('retrieval_attempt', 1)
        print(f"Retrieval attempt: {attempt}")
    
    elif step == "DRAFT_GENERATION":
        draft = state.get('draft_response', '')
        print(f"Draft preview: {draft[:150]}...")
    
    elif step == "REVIEW":
        passed = state.get('review_passed', False)
        feedback = state.get('reviewer_feedback', '')
        attempt = state.get('draft_attempt', 1)
        print(f"Review passed: {passed}")
        print(f"Draft attempt: {attempt}")
        if feedback:
            print(f"Feedback: {feedback[:100]}...")
    
    elif step == "FINAL":
        escalated = state.get('escalated', False)
        max_attempts = state.get('max_attempts_reached', False)
        
        if escalated:
            print("❌ TICKET ESCALATED - Max attempts reached")
        elif state.get('review_passed', False):
            print("✅ TICKET RESOLVED - Response approved")
        else:
            print("⚠️ UNKNOWN STATE")


def run_single_ticket(graph, subject: str, description: str) -> Dict[str, Any]:
    """Run a single ticket through the workflow"""
    print(f"\n🎫 PROCESSING NEW TICKET")
    print(f"Subject: {subject}")
    print(f"Description: {description[:100]}...")
    
    # Create initial state
    initial_state = create_initial_state(subject, description)
    print_state_summary(initial_state, "INPUT")
    
    try:
        # Run the workflow
        logger.info(f"Starting workflow for ticket: {subject}")
        
        # Execute the graph
        final_state = graph.invoke(initial_state)
        
        # Print final results
        print_state_summary(final_state, "FINAL")
        
        # Return summary
        return {
            "success": True,
            "classification": final_state.get('classification'),
            "escalated": final_state.get('escalated', False),
            "review_passed": final_state.get('review_passed', False),
            "attempts": final_state.get('draft_attempt', 1),
            "final_state": final_state
        }
        
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}")
        print(f"❌ ERROR: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "final_state": initial_state
        }


        




def run_interactive_mode(graph):
    """Run in interactive mode for manual testing"""
    print("\n" + "="*60)
    print("🎯 INTERACTIVE MODE")
    print("="*60)
    print("Enter your own support tickets to test the system")
    print("Type 'quit' to exit")
    
    while True:
        print("\n" + "-"*40)
        subject = input("Enter ticket subject: ").strip()
        
        if subject.lower() in ['quit', 'exit', 'q']:
            break
            
        if not subject:
            print("Subject cannot be empty!")
            continue
            
        description = input("Enter ticket description: ").strip()
        
        if not description:
            print("Description cannot be empty!")
            continue
        
        # Process the ticket
        result = run_single_ticket(graph, subject, description)
        
        if result["success"]:
            final_state = result["final_state"]
            
            if result["review_passed"]:
                print(f"\n✅ FINAL RESPONSE:")
                print("-" * 30)
                print(final_state.get('draft_response', 'No response generated'))
            elif result["escalated"]:
                print(f"\n⚠️ TICKET ESCALATED - Human review required")
            
        print(f"\nContinue testing? (Press Enter to continue, 'q' to quit)")
        if input().lower().strip() in ['q', 'quit']:
            break


def main():
    """Main application entry point"""
    print("🤖 Support Ticket Resolution Agent")
    print("Built with LangGraph")
    print("="*50)
    
    try:
        
        print("Initializing LangGraph workflow...")
        graph = create_support_graph()
        print(" Graph initialized successfully!")

        required_env_vars = ["GROQ_API_KEY"]
      
        # Show menu 
        while True:
            print("\n" + "="*50)
            print("Choose an option:")
            print("1. Run interactive mode (enter your own tickets)")
            print("2. Run single sample ticket")
            print("3. Quit")
            print("="*50)
            
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                  run_interactive_mode(graph)
            elif choice == "2":
                test_tickets = create_test_tickets()
                ticket = test_tickets[0]  # First sample ticket
                run_single_ticket(graph, ticket["subject"], ticket["description"])

            elif choice == "3":
                 break   
            else:
                print("Invalid choice! Please enter 1-4.")
        
        print("\n👋 Thanks for using the Support Ticket Agent!")
        
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        print("\nPlease check:")
        print("1. All required files are present")
        print("2. Environment variables are set")
        print("3. Dependencies are installed")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())