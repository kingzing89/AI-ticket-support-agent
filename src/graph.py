# src/graph.py
import logging
from typing import Dict
from langgraph.graph import StateGraph, END
from .state import SupportTicketState
from classifier import classify_ticket_node
from .rag_retrieval import RAGRetriever
from .draft import draft_generation_node
from .review import review_node
from .escalation_logger import escalation_node_with_logging

logger = logging.getLogger(__name__)


def rag_retrieval_node(state: SupportTicketState) -> Dict:
    
    retriever = RAGRetriever()
    
   
    attempt = state.get('retrieval_attempt', 1)
    
   
    retrieved_docs = retriever.retrieve_context(
        classification=state['classification'],
        subject=state['subject'],
        description=state['description'],
        reviewer_feedback=state.get('reviewer_feedback'),
        attempt=attempt
    )
    
  
    formatted_context = retriever.format_context_for_prompt(retrieved_docs)
    
    logger.info(f"RAG retrieval completed, attempt {attempt}")
    
    return {
        "retrieved_context": retrieved_docs,
        "formatted_context": formatted_context,
        "retrieval_attempt": attempt,
        "draft_attempt": 1  
    }


def retry_rag_node(state: SupportTicketState) -> Dict:
   
    retriever = RAGRetriever()
    
    
    attempt = state.get('retrieval_attempt', 1) + 1
    
    logger.info(f"Retry RAG retrieval, attempt {attempt}")
    
  
    retrieved_docs = retriever.retrieve_context(
        classification=state['classification'],
        subject=state['subject'],
        description=state['description'],
        reviewer_feedback=state.get('reviewer_feedback'),
        attempt=attempt
    )
    
 
    formatted_context = retriever.format_context_for_prompt(retrieved_docs)
    
    return {
        "retrieved_context": retrieved_docs,
        "formatted_context": formatted_context,
        "retrieval_attempt": attempt
    }


def retry_draft_node(state: SupportTicketState) -> Dict:
    
    from .draft import DraftGenerator
    
    generator = DraftGenerator()
    
   
    attempt = state.get('draft_attempt', 1) + 1
    
    logger.info(f"Retry draft generation, attempt {attempt}")
    
    
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
  
    attempt = state.get('draft_attempt', 1)
    review_passed = state.get('review_passed', False)
    
    logger.info(f"Checking attempts: {attempt}, review_passed: {review_passed}")
    
    if review_passed:
        return "approved"
    elif attempt >= 3:  
        logger.warning("Maximum attempts reached, escalating")
        return "max_attempts_reached"
    else:
        logger.info("Retrying after failed review")
        return "retry"


# def escalation_node(state: SupportTicketState) -> Dict:
   
#     logger.info("Escalating ticket after max attempts reached")
    
#     escalation_message = f"""This ticket has been escalated for human review after failing automated processing.

# Original Ticket:
# Subject: {state['subject']}  
# Description: {state['description']}
# Classification: {state['classification']}

# Attempts Made: {state.get('draft_attempt', 1)}
# Failed Draft: {state.get('draft_response', 'No draft generated')}
# Final Reviewer Feedback: {state.get('reviewer_feedback', 'No feedback available')}

# Please review and respond manually."""
    
#     return {
#         "escalated": True,
#         "max_attempts_reached": True,
#         "escalation_message": escalation_message
#     }


def create_support_graph():
   
    
    logger.info("Creating support ticket resolution graph")
    
    
    graph = StateGraph(SupportTicketState)
    
   
    graph.add_node("classify_ticket", classify_ticket_node)
    graph.add_node("rag_retrieval", rag_retrieval_node)
    graph.add_node("draft_response", draft_generation_node)
    graph.add_node("review_draft", review_node)
    graph.add_node("retry_rag", retry_rag_node)
    graph.add_node("retry_draft", retry_draft_node)
    graph.add_node("escalation", escalation_node_with_logging)
    
    
    graph.set_entry_point("classify_ticket")
    graph.add_edge("classify_ticket", "rag_retrieval")
    graph.add_edge("rag_retrieval", "draft_response")
    graph.add_edge("draft_response", "review_draft")
    
   
    graph.add_conditional_edges(
        "review_draft",
        check_max_attempts,
        {
            "approved": END,
            "retry": "retry_rag", 
            "max_attempts_reached": "escalation"
        }
    )
    
   
    graph.add_edge("retry_rag", "retry_draft")
    graph.add_edge("retry_draft", "review_draft")
    
  
    graph.add_edge("escalation", END)
    
    logger.info("Graph structure defined, compiling...")
    
    try:
        compiled_graph = graph.compile()
        logger.info("Graph compiled successfully")
        return compiled_graph
    except Exception as e:
        logger.error(f"Failed to compile graph: {str(e)}")
        raise



def test_graph_creation():
    """Test that the graph can be created and compiled successfully"""
    try:
        graph = create_support_graph()
        print("✅ Graph created and compiled successfully!")
        
        # Try to get the graph structure
        print("\n📊 Graph Structure:")
        print(f"Nodes: {list(graph.get_graph().nodes())}")
        print(f"Entry points: {graph.get_graph().entry_points}")
        
        return True
    except Exception as e:
        print(f"❌ Graph creation failed: {str(e)}")
        return False


if __name__ == "__main__":
    
    test_graph_creation()