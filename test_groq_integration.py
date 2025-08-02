# test_groq_integration.py
import os
from dotenv import load_dotenv
from src.groq_client import test_groq_client
from src.draft import test_draft_generation
from src.graph import create_support_graph

# Load environment variables
load_dotenv()

def test_groq_api_key():
    """Test if Groq API key is properly configured"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        print("Please add it to your .env file:")
        print("GROQ_API_KEY=your_groq_api_key_here")
        return False
    else:
        print(f"✅ GROQ_API_KEY found (starts with: {api_key[:10]}...)")
        return True

def test_full_pipeline_with_groq():
    """Test the full pipeline using Groq LLM"""
    print("=== Testing Full Pipeline with Groq ===")
    
    if not test_groq_api_key():
        return
    
    # Create the graph
    graph = create_support_graph()
    
    # Test cases
    test_cases = [
        {
            "subject": "Billing issue with refund",
            "description": "I was charged twice for my subscription this month. I need one of the charges refunded.",
            "expected_category": "billing"
        },
        {
            "subject": "Password reset not working",
            "description": "I clicked forgot password but never received the reset email. I checked spam folder too.",
            "expected_category": "technical"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Subject: {test_case['subject']}")
        print(f"Description: {test_case['description']}")
        print(f"Expected Category: {test_case['expected_category']}")
        
        # Initial state
        initial_state = {
            "subject": test_case['subject'],
            "description": test_case['description'],
            "classification": None,
            "retrieved_context": None,
            "formatted_context": None,
            "retrieval_attempt": None,
            "draft_response": None
        }
        
        try:
            # Run the graph
            print("\nRunning pipeline...")
            result = graph.invoke(initial_state)
            
            print(f"\n✅ Results:")
            print(f"   Classification: {result['classification']}")
            print(f"   Documents Retrieved: {len(result.get('retrieved_context', []))}")
            print(f"   Draft Generated: {'Yes' if result.get('draft_response') else 'No'}")
            
            if result.get('draft_response'):
                print(f"\n📝 Generated Draft Response:")
                print("-" * 50)
                print(result['draft_response'])
                print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("\n" + "="*60)

def main():
    """Main test function"""
    print("🚀 Testing Groq Integration for Support Agent")
    print("=" * 60)
    
    # Test 1: API key configuration
    print("\n1. Testing API Key Configuration...")
    if not test_groq_api_key():
        return
    
    # Test 2: Basic Groq client
    print("\n2. Testing Basic Groq Client...")
    if not test_groq_client():
        return
    
    # Test 3: Draft generation standalone
    print("\n3. Testing Draft Generation...")
    try:
        test_draft_generation()
        print("✅ Draft generation test completed")
    except Exception as e:
        print(f"❌ Draft generation test failed: {str(e)}")
        return
    
    # Test 4: Full pipeline
    print("\n4. Testing Full Pipeline...")
    test_full_pipeline_with_groq()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()