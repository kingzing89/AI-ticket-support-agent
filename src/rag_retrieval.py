# src/rag_retrieval.py
from typing import List, Dict
import logging

# Mock knowledge base - you can expand this or load from files
KNOWLEDGE_BASE = {
    "billing": [
        {
            "title": "Payment Method Issues",
            "content": "If you're experiencing payment method issues, please verify that your card details are correct and not expired. You can update your payment method in the billing section of your account settings."
        },
        {
            "title": "Refund Policy",
            "content": "Refunds are processed within 3-5 business days after approval. To request a refund, please provide your order number and reason for the refund request."
        },
        {
            "title": "Subscription Management",
            "content": "You can upgrade, downgrade, or cancel your subscription at any time. Changes take effect at the next billing cycle unless you're upgrading, which is immediate."
        },
        {
            "title": "Invoice Questions",
            "content": "All invoices are sent to your registered email address. You can also download them from the billing section of your account. If you need a specific invoice format, please contact our billing team."
        }
    ],
    "technical": [
        {
            "title": "Login Issues",
            "content": "For login problems, first try clearing your browser cache and cookies. If that doesn't work, try resetting your password. Make sure you're using the correct email address associated with your account."
        },
        {
            "title": "Mobile App Crashes",
            "content": "If the mobile app is crashing, try updating to the latest version from your app store. If the problem persists, try restarting your device or reinstalling the app."
        },
        {
            "title": "API Integration",
            "content": "Our API has a rate limit of 1000 requests per hour. Make sure you're including your API key in the headers and following our authentication guidelines in the documentation."
        },
        {
            "title": "Browser Compatibility",
            "content": "Our platform is compatible with Chrome 90+, Firefox 88+, Safari 14+, and Edge 90+. Please ensure you're using a supported browser version for the best experience."
        }
    ],
    "security": [
        {
            "title": "Password Reset",
            "content": "To reset your password, click the 'Forgot Password' link on the login page. You'll receive an email with reset instructions. The reset link expires after 24 hours for security."
        },
        {
            "title": "Two-Factor Authentication",
            "content": "We highly recommend enabling 2FA for your account security. You can set this up in your account security settings using an authenticator app or SMS."
        },
        {
            "title": "Suspicious Activity",
            "content": "If you notice any suspicious activity on your account, immediately change your password and contact our security team. We monitor all accounts for unusual login patterns."
        },
        {
            "title": "Data Privacy",
            "content": "We follow strict data privacy guidelines and never share your personal information with third parties without your consent. You can review our privacy policy for complete details."
        }
    ],
    "general": [
        {
            "title": "Support Hours",
            "content": "Our customer support team is available Monday through Friday, 9 AM to 6 PM EST. For urgent issues outside these hours, please use our emergency contact form."
        },
        {
            "title": "Feature Requests",
            "content": "We love hearing your ideas! You can submit feature requests through our feedback form in your account dashboard. Our product team reviews all suggestions monthly."
        },
        {
            "title": "Account Deletion",
            "content": "Account deletion is permanent and cannot be undone. If you proceed, all your data will be removed within 48 hours. Please download any important data before requesting deletion."
        },
        {
            "title": "Getting Started Guide",
            "content": "New to our platform? Check out our getting started guide in the help center. It covers account setup, basic features, and common workflows to help you get up and running quickly."
        }
    ]
}

class RAGRetriever:
    def __init__(self):
        self.knowledge_base = KNOWLEDGE_BASE
        self.logger = logging.getLogger(__name__)
    
    def retrieve_context(self, classification: str, subject: str, description: str, 
                        reviewer_feedback: str = None, attempt: int = 1) -> List[Dict]:
        """
        Retrieve relevant context based on classification and query
        
        Args:
            classification: The ticket category (billing, technical, security, general)
            subject: Ticket subject line
            description: Ticket description
            reviewer_feedback: Feedback from previous review (for retries)
            attempt: Current attempt number (1, 2, or 3)
        
        Returns:
            List of relevant documents with title and content
        """
        self.logger.info(f"Retrieving context for category: {classification}, attempt: {attempt}")
        
        # Normalize classification
        category = classification.lower()
        if category not in self.knowledge_base:
            self.logger.warning(f"Unknown category: {category}, defaulting to general")
            category = "general"
        
        # Create search query
        query_text = f"{subject} {description}".lower()
        if reviewer_feedback:
            query_text += f" {reviewer_feedback}".lower()
        
        # Get documents for the category
        category_docs = self.knowledge_base[category]
        
        # Score documents based on keyword overlap
        scored_docs = []
        query_words = set(query_text.split())
        
        for doc in category_docs:
            # Calculate relevance score
            doc_text = f"{doc['title']} {doc['content']}".lower()
            doc_words = set(doc_text.split())
            
            # Simple overlap scoring
            overlap = len(query_words.intersection(doc_words))
            total_query_words = len(query_words)
            score = overlap / total_query_words if total_query_words > 0 else 0
            
            scored_docs.append((doc, score))
        
        # Sort by relevance score
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Determine how many docs to return based on attempt
        if attempt == 1:
            # First attempt: return top 2 most relevant
            num_docs = 2
        elif attempt == 2:
            # Second attempt: return top 3 (broader context)
            num_docs = 3
        else:
            # Final attempt: return all docs for the category
            num_docs = len(scored_docs)
        
        # Return selected documents
        selected_docs = [doc for doc, score in scored_docs[:num_docs]]
        
        self.logger.info(f"Retrieved {len(selected_docs)} documents for {category}")
        return selected_docs
    
    def format_context_for_prompt(self, documents: List[Dict]) -> str:
        """
        Format retrieved documents for use in LLM prompts
        """
        if not documents:
            return "No relevant documentation found."
        
        formatted_context = "Relevant Documentation:\n\n"
        for i, doc in enumerate(documents, 1):
            formatted_context += f"{i}. **{doc['title']}**\n"
            formatted_context += f"   {doc['content']}\n\n"
        
        return formatted_context


# Test function to verify your RAG is working
def test_rag_retrieval():
    """
    Test function to verify RAG retrieval works correctly
    """
    retriever = RAGRetriever()
    
    # Test cases
    test_cases = [
        {
            "classification": "billing",
            "subject": "Refund request",
            "description": "I want to cancel my subscription and get a refund"
        },
        {
            "classification": "technical", 
            "subject": "Can't login",
            "description": "I'm having trouble logging into my account"
        },
        {
            "classification": "security",
            "subject": "Password reset",
            "description": "I forgot my password and need to reset it"
        }
    ]
    
    for test in test_cases:
        print(f"\n=== Testing {test['classification']} ===")
        print(f"Subject: {test['subject']}")
        print(f"Description: {test['description']}")
        
        docs = retriever.retrieve_context(**test)
        formatted = retriever.format_context_for_prompt(docs)
        
        print(f"Retrieved {len(docs)} documents:")
        print(formatted)

if __name__ == "__main__":
    test_rag_retrieval()