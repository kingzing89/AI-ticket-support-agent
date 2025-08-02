#!/usr/bin/env python3
"""
Test script for the classification functionality
Tests both the standalone classifier and the LangGraph node integration
"""

from models import create_initial_state, TicketCategory
from input_handler import handle_input_ticket
from classifier import classify_ticket_node, TicketClassifier, is_classification_reliable


def test_standalone_classifier():
    """Test the classifier directly without LangGraph"""
    print("🧪 Testing Standalone Classifier")
    print("=" * 50)
    
    classifier = TicketClassifier()
    
    test_cases = [
        # Billing examples
        {
            "subject": "Refund request for overcharge",
            "description": "I was charged $199 instead of $99 for my subscription. Please process a refund for the difference.",
            "expected": TicketCategory.BILLING,
            "category": "Billing"
        },
        
        # Technical examples
        {
            "subject": "Login error 403",
            "description": "I'm getting error code 403 when trying to log in. The app worked fine yesterday but now it's broken.",
            "expected": TicketCategory.TECHNICAL,
            "category": "Technical"
        },
        
        # Security examples
        {
            "subject": "Password reset not working",
            "description": "I forgot my password and tried to reset it, but I'm not receiving the reset email. My account might be compromised.",
            "expected": TicketCategory.SECURITY,
            "category": "Security"
        },
        
        # General examples
        {
            "subject": "Question about premium features",
            "description": "I'm interested in upgrading to premium. Can you tell me what additional features I would get?",
            "expected": TicketCategory.GENERAL,
            "category": "General"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- {case['category']} Test {i} ---")
        print(f"Subject: {case['subject']}")
        print(f"Description: {case['description'][:80]}...")
        
        result = classifier.classify_ticket(case['subject'], case['description'])
        
        is_correct = result.category == case['expected']
        status = "✅ CORRECT" if is_correct else "❌ INCORRECT"
        
        print(f"Expected: {case['expected'].value}")
        print(f"Predicted: {result.category.value}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Status: {status}")
        
        if result.confidence < 0.5:
            print("⚠️ Low confidence - might need manual review")


def test_classification_node():
    """Test the LangGraph classification node"""
    print("\n🧪 Testing Classification Node Integration")
    print("=" * 50)
    
    # Test case: typical support ticket
    subject = "Cannot access billing dashboard"
    description = "I'm trying to view my billing history but the dashboard won't load. I get a timeout error after waiting 30 seconds."
    
    print(f"Input Ticket:")
    print(f"  Subject: {subject}")
    print(f"  Description: {description}")
    
    # Create initial state and process through input handler
    state = create_initial_state(subject, description)
    state = handle_input_ticket(state)
    
    print(f"\nBefore Classification:")
    print(f"  Classification: {state.get('classification', 'None')}")
    print(f"  Processing logs: {len(state['processing_log'])}")
    
    # Run classification node
    classified_state = classify_ticket_node(state)
    
    print(f"\nAfter Classification:")
    print(f"  Classification: {classified_state['classification']}")
    print(f"  Confidence: {classified_state.get('classification_metadata', {}).get('confidence', 'N/A')}")
    print(f"  Reliable: {is_classification_reliable(classified_state)}")
    
    print(f"\nProcessing Log:")
    for log_entry in classified_state['processing_log']:
        print(f"  - {log_entry}")
    
    # Test metadata
    metadata = classified_state.get('classification_metadata', {})
    if metadata:
        print(f"\nClassification Metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")


def test_edge_cases():
    """Test classification with edge cases and ambiguous tickets"""
    print("\n🧪 Testing Edge Cases")
    print("=" * 50)
    
    edge_cases = [
        {
            "subject": "Issue",
            "description": "I have an issue",
            "name": "Extremely vague ticket"
        },
        {
            "subject": "Billing and technical problem",
            "description": "My payment failed and now I can't access the app. Is this related to the billing issue or a technical problem?",
            "name": "Multi-category ticket"
        },
        {
            "subject": "URGENT: HELP NEEDED ASAP!!!",
            "description": "Everything is broken and I need help immediately! This is critical for my business!",
            "name": "High urgency, no specifics"
        },
        {
            "subject": "",
            "description": "password reset login issue billing question general help",
            "name": "Empty subject, keyword soup"
        }
    ]
    
    classifier = TicketClassifier()
    
    for i, case in enumerate(edge_cases, 1):
        print(f"\n--- Edge Case {i}: {case['name']} ---")
        print(f"Subject: '{case['subject']}'")
        print(f"Description: '{case['description']}'")
        
        try:
            result = classifier.classify_ticket(case['subject'], case['description'])
            
            print(f"Classification: {result.category.value}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Fallback used: {result.fallback_used}")
            print(f"Reasoning: {result.reasoning}")
            
            if result.confidence < 0.4:
                print("⚠️ Very low confidence - manual review recommended")
            elif result.fallback_used:
                print("ℹ️ Fallback classification used")
                
        except Exception as e:
            print(f"❌ Error during classification: {e}")


def test_classification_consistency():
    """Test that similar tickets get consistent classifications"""
    print("\n🧪 Testing Classification Consistency")
    print("=" * 50)
    
    # Similar tickets that should get the same classification
    similar_tickets = [
        {
            "group": "Login Issues",
            "expected": TicketCategory.SECURITY,
            "tickets": [
                ("Can't log in", "I can't log into my account with my usual password"),
                ("Login not working", "My login credentials aren't working anymore"),
                ("Access denied", "I'm getting access denied when trying to log in")
            ]
        },
        {
            "group": "Billing Questions", 
            "expected": TicketCategory.BILLING,
            "tickets": [
                ("Charge question", "I have a question about a charge on my card"),
                ("Payment inquiry", "I need help understanding my recent payment"),
                ("Invoice help", "Can you help me understand my invoice?")
            ]
        }
    ]
    
    classifier = TicketClassifier()
    
    for group_data in similar_tickets:
        print(f"\n--- Testing {group_data['group']} ---")
        print(f"Expected category: {group_data['expected'].value}")
        
        results = []
        for subject, description in group_data['tickets']:
            result = classifier.classify_ticket(subject, description)
            results.append(result)
            
            correct = result.category == group_data['expected']
            status = "✅" if correct else "❌"
            print(f"  {status} '{subject}' → {result.category.value} (conf: {result.confidence:.2f})")
        
        # Check consistency
        categories = [r.category for r in results]
        is_consistent = len(set(categories)) == 1
        print(f"  Consistency: {'✅ Consistent' if is_consistent else '❌ Inconsistent'}")


def test_full_workflow():
    """Test the complete workflow from input to classification"""
    print("\n🧪 Testing Full Input → Classification Workflow")
    print("=" * 60)
    
    # Realistic test ticket
    subject = "Mobile app login problems after password change"
    description = """I changed my password yesterday through the web interface, but now I can't log into the mobile app. 
    It keeps saying 'invalid credentials' even though I'm using the new password that works on the website. 
    I've tried clearing the app cache and reinstalling, but the problem persists. 
    This is urgent as I need access for a client presentation tomorrow."""
    
    print(f"Test Ticket:")
    print(f"Subject: {subject}")
    print(f"Description: {description[:100]}...")
    
    try:
        # Step 1: Create initial state
        print(f"\n📥 Step 1: Input Processing")
        state = create_initial_state(subject, description, priority="high")
        print(f"  ✅ Initial state created: {state['ticket'].ticket_id}")
        
        # Step 2: Input handling
        print(f"\n🔄 Step 2: Input Handler")
        state = handle_input_ticket(state)
        print(f"  ✅ Input processed and validated")
        
        # Step 3: Classification
        print(f"\n🏷️ Step 3: Classification")
        state = classify_ticket_node(state)
        print(f"  ✅ Classified as: {state['classification']}")
        
        # Show final results
        print(f"\n📊 Final Results:")
        print(f"  Ticket ID: {state['ticket'].ticket_id}")
        print(f"  Classification: {state['classification']}")
        print(f"  Confidence: {state.get('classification_metadata', {}).get('confidence', 'N/A'):.2f}")
        print(f"  Reliable: {is_classification_reliable(state)}")
        
        print(f"\n📝 Processing History:")
        for i, log in enumerate(state['processing_log'], 1):
            print(f"  {i}. {log}")
        
        # This state is now ready for the next step (RAG retrieval)
        print(f"\n✅ State ready for next step (RAG retrieval)")
        print(f"   Classification will influence context retrieval: {state['classification']}")
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")


def main():
    """Run all classification tests"""
    print("🎯 Support Ticket Classification - Test Suite")
    print("=" * 70)
    
    test_standalone_classifier()
    test_classification_node()
    test_edge_cases()
    test_classification_consistency()
    test_full_workflow()
    
    print(f"\n🏁 All classification tests completed!")
    print("=" * 70)
    print("\n💡 Next step: Implement RAG Context Retrieval based on classification results")


if __name__ == "__main__":
    main()