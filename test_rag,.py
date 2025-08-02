# test_rag.py
from src.rag_retrieval import test_rag_retrieval
from src.graph import create_support_graph

def test_rag_integration():
    """Test RAG integration with the full graph"""
    print("=== Testing RAG Integration ===")
    
    # Create the graph
    graph = create_support_graph()
    
    # Test with a sample ticket
    initial_state = {
        "subject": "Can't access my account",
        "description": "I forgot my password and can't login to my account. I tried the forgot password link but didn't receive any email.",
        "classification": None,
        "retrieved_context": None,
        "formatted_context": None,
        "retrieval_attempt": None
    }
    
    # Run the graph
    result = graph.invoke(initial_state)
    
    print(f"Classification: {result['classification']}")
    print(f"Retrieved {len(result['retrieved_context'])} documents")
    print(f"Formatted context:\n{result['formatted_context']}")

if __name__ == "__main__":
    # Test standalone RAG
    print("=== Testing Standalone RAG ===")
    test_rag_retrieval()
    
    print("\n" + "="*50 + "\n")
    
    # Test integrated RAG
    test_rag_integration()