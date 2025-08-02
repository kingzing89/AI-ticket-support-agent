# test_full_pipeline.py
import os
from dotenv import load_dotenv
from src.graph import create_support_graph
from src.review import test_draft_review

# Load environment variables
load_dotenv()

def test_review_functionality():
    """Test the review functionality standalone"""
    print("=== Testing Review Functionality ===")
    try:
        test_draft_review()
        return True
    except Exception as e:
        print(f"❌ Review test failed: {str(e)}")
        return False

def test_complete_pipeline():
    """Test the complete pipeline with review and retry logic"""
    print("=== Testing Complete Pipeline with Review ===")
    
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found")
        return
    
    graph = create_support_graph()
    
    # Test cases designed to potentially trigger retries
    test_cases = [
        {
            "name": "Good Technical Issue",
            "subject": "Can't log into my account",
            "description": "I'm having trouble logging in. I tried my password multiple times but it keeps saying invalid credentials. I also tried the forgot password link but haven't received an email yet.",
            "expected_approval": True
        },
        {
            "name": "Complex Billing Issue", 
            "subject": "Double charged for subscription",
            "description": "I was charged twice for my monthly subscription. One charge was on the 1st and another on the 3rd. I need one of them refunded immediately.",
            "expected_approval": False  # Might trigger retry due to refund promise concerns
        },
        {
            "name": "Security Concern",
            "subject": "Suspicious login attempts",
            "description": "I received 5 emails about failed login attempts from different countries. I'm worried my account is compromised.",
            "expected_approval": True  # Should be handled well
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Subject: {test_case['subject']}")
        print(f"Description: {test_case['description']}")
        
        initial_state = {
            "subject": test_case['subject'],
            "description": test_case['description'],
            "classification": None,
            "retrieved_context": None,
            "formatted_context": None,
            "retrieval_attempt": None,
            "draft_response": None,
            "review_passed": None,
            "reviewer_feedback": None,
            "draft_attempt": None,
            "escalated": None,
            "max_attempts_reached": None
        }
        
        try:
            print("🔄 Running pipeline...")
            result = graph.invoke(initial_state)
            
            print(f"\n📊 Results:")
            print(f"   Classification: {result.get('classification', 'N/A')}")
            print(f"   Draft Attempts: {result.get('draft_attempt', 1)}")
            print(f"   Review Passed: {result.get('review_passed', False)}")
            print(f"   Escalated: {result.get('escalated', False)}")
            
            if result.get('review_passed'):
                print(f"\n✅ Final Approved Response:")
                print("-" * 50)
                print(result.get('draft_response', 'No response'))
                print("-" * 50)
            elif result.get('escalated'):
                print(f"\n⚠️ Ticket Escalated:")
                print("-" * 50)
                print(result.get('escalation_message', 'No escalation message'))
                print("-" * 50)
            else:
                print(f"\n❌ Unexpected State:")
                print(f"   Last Reviewer Feedback: {result.get('reviewer_feedback', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Pipeline failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80)

def test_retry_mechanism():
    """Test the retry mechanism specifically"""
    print("=== Testing Retry Mechanism ===")
    
    # This is a case designed to potentially fail initial review
    test_case = {
        "subject": "Need immediate refund",
        "description": "I want my money back right now. Cancel everything and refund all charges from the past 6 months.",
        "classification": "billing"
    }
    
    graph = create_support_graph()
    
    initial_state = {
        "subject": test_case["subject"],
        "description": test_case["description"],
        "classification": None,
        "retrieved_context": None,
        "formatted_context": None,
        "retrieval_attempt": None,
        "draft_response": None,
        "review_passed": None,
        "reviewer_feedback": None,
        "draft_attempt": None,
        "escalated": None,
        "max_attempts_reached": None
    }
    
    try:
        result = graph.invoke(initial_state)
        
        print(f"Final attempt count: {result.get('draft_attempt', 1)}")
        print(f"Review passed: {result.get('review_passed', False)}")
        print(f"Escalated: {result.get('escalated', False)}")
        
        if result.get('draft_attempt', 1) > 1:
            print("✅ Retry mechanism was triggered!")
        else:
            print("ℹ️ No retries needed")
            
    except Exception as e:
        print(f"❌ Retry test failed: {str(e)}")

def main():
    """Main test runner"""
    print("🧪 Testing Complete Support Agent Pipeline")
    print("=" * 60)
    
    # Test 1: Review functionality
    print("\n1. Testing Review Component...")
    if not test_review_functionality():
        return
    
    # Test 2: Complete pipeline  
    print("\n2. Testing Complete Pipeline...")
    test_complete_pipeline()
    
    # Test 3: Retry mechanism
    print("\n3. Testing Retry Mechanism...")
    test_retry_mechanism()
    
    print("\n🎉 All pipeline tests completed!")

if __name__ == "__main__":
    main()