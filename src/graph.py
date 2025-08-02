# src/graph.py
from langgraph.graph import StateGraph
from .state import SupportTicketState
from classifier import classify_ticket_node as classify_ticket
from .rag_retrieval import RAGRetriever
from .draft import draft_generation_node
from .review import review_node  # ADD THIS IMPORT

# ADD THIS NEW NODE FUNCTION
def retry_rag_node(state: SupportTicketState) -> dict:
    """
    Enhanced RAG node for retries that uses reviewer feedback
    """
    retriever = RAGRetriever()
    
    # Increment attempt counter
    attempt = state.get('retrieval_attempt', 1) + 1
    
    # Retrieve context with reviewer feedback incorporated
    retrieved_docs = retriever.retrieve_context(
        classification=state['classification'],
        subject=state['subject'],
        description=state['description'],
        reviewer_feedback=state.get('reviewer_feedback'),
        attempt=attempt
    )
    
    # Format context for prompt use
    formatted_context = retriever.format_context_for_prompt(retrieved_docs)
    
    return {
        "retrieved_context": retrieved_docs,
        "formatted_context": formatted_context,
        "retrieval_attempt": attempt
    }

def retry_draft_node(state: SupportTicketState) -> dict:
    """
    Enhanced draft node for retries that incorporates reviewer feedback
    """
    from .draft import DraftGenerator
    
    generator = DraftGenerator()
    
    # Increment attempt counter
    attempt = state.get('draft_attempt', 1) + 1
    
    # Generate draft with reviewer feedback
    draft = generator.generate_draft(
        subject=state['subject'],
        description=state['description'],
        classification=state['classification'],
        formatted_context=state['formatted_context'],
        reviewer_feedback=state.get('reviewer_feedback'),
        attempt=attempt
    )
    
    return {
        "draft_response": draft,
        "draft_attempt": attempt
    }

def check_max_attempts(state: SupportTicketState) -> str:
    """
    Check if we've reached maximum attempts and route accordingly
    """
    attempt = state.get('draft_attempt', 1)
    review_passed = state.get('review_passed', False)
    
    if review_passed:
        return "approved"
    elif attempt >= 3:  # Maximum 3 attempts (original + 2 retries)
        return "max_attempts_reached"
    else:
        return "retry"
def rag_retrieval_node(state: SupportTicketState) -> dict:
    """
    Node to retrieve relevant context based on classification
    """
    retriever = RAGRetriever()
    
    # Get the current attempt number (for retry logic)
    attempt = state.get('retrieval_attempt', 1)
    
    # Retrieve context
    retrieved_docs = retriever.retrieve_context(
        classification=state['classification'],
        subject=state['subject'],
        description=state['description'],
        reviewer_feedback=state.get('reviewer_feedback'),
        attempt=attempt
    )
    
    # Format context for prompt use
    formatted_context = retriever.format_context_for_prompt(retrieved_docs)
    
    return {
        "retrieved_context": retrieved_docs,
        "formatted_context": formatted_context,
        "retrieval_attempt": attempt,
        "draft_attempt": 1  # Initialize draft attempt counter
    }

def escalation_node(state: SupportTicketState) -> dict:
    """
    Node to handle escalation when max attempts reached
    """
    logging.getLogger(__name__).info("Escalating ticket after max attempts reached")
    
    escalation_message = f"""This ticket has been escalated for human review after failing automated processing.

Original Ticket:
Subject: {state['subject']}  
Description: {state['description']}
Classification: {state['classification']}

Failed Draft: {state.get('draft_response', 'No draft generated')}
Final Reviewer Feedback: {state.get('reviewer_feedback', 'No feedback available')}

Please review and respond manually."""
    
    return {
        "escalated": True,
        "max_attempts_reached": True,
        "escalation_message": escalation_message
    }

def create_support_graph():
    # Create the graph
    graph = StateGraph(SupportTicketState)
    
    # Add nodes
    graph.add_node("classify_ticket", classify_ticket)
    graph.add_node("rag_retrieval", rag_retrieval_node)
    graph.add_node("draft_response", draft_generation_node)
    graph.add_node("review_draft", review_node)  # ADD THIS LINE
    graph.add_node("retry_rag", retry_rag_node)  # ADD THIS LINE
    graph.add_node("retry_draft", retry_draft_node)  # ADD THIS LINE  
    graph.add_node("escalation", escalation_node)  # ADD THIS LINE
    
    # Define the flow
    graph.set_entry_point("classify_ticket")
    graph.add_edge("classify_ticket", "rag_retrieval")
    graph.add_edge("rag_retrieval", "draft_response")
    graph.add_edge("draft_response", "review_draft")
    
    # Add conditional routing after review
    graph.add_conditional_edges(
        "review_draft",
        check_max_attempts,
        {
            "approved": END,
            "retry": "retry_rag", 
            "max_attempts_reached": "escalation"
        }
    )
    
    # Retry flow
    graph.add_edge("retry_rag", "retry_draft")
    graph.add_edge("retry_draft", "review_draft")
    
    # Escalation ends the flow
    graph.add_edge("escalation", END)
    
    return graph.compile()