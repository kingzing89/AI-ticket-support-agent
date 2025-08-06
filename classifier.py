"""
Simple Ticket Classifier - Easy to understand version
This classifier sorts support tickets into 4 categories based on keywords
"""

import logging
from typing import Dict, List
from src.models import TicketCategory

logger = logging.getLogger(__name__)


class SimpleTicketClassifier:
    """
    A simple ticket classifier that looks for specific words to categorize tickets
    """
    
    def __init__(self):
        # Keywords for each category - if we find these words, we classify accordingly
        self.keywords = {
            TicketCategory.BILLING: [
                'billing', 'payment', 'charge', 'invoice', 'refund', 
                'subscription', 'money', 'credit card', 'cost', 'price'
            ],
            
            TicketCategory.TECHNICAL: [
                'error', 'bug', 'crash', 'broken', 'not working', 
                'website down', 'app crashed', 'slow', 'loading'
            ],
            
            TicketCategory.SECURITY: [
                'password', 'login', 'access', 'hacked', 'locked out',
                'can\'t login', 'forgot password', 'account locked'
            ],
            
            TicketCategory.GENERAL: [
                'question', 'help', 'how to', 'information', 
                'feature request', 'general inquiry'
            ]
        }
    
    def classify_ticket(self, subject: str, description: str) -> Dict:
       
       
        full_text = f"{subject} {description}".lower()
        
       
        category_scores = {}
        
        for category, keyword_list in self.keywords.items():
            score = 0
            found_keywords = []
            
           
            for keyword in keyword_list:
                if keyword in full_text:
                    score += 1
                    found_keywords.append(keyword)
            
            category_scores[category] = {
                'score': score,
                'keywords': found_keywords
            }
        
        
        best_category = None
        best_score = 0
        
        for category, data in category_scores.items():
            if data['score'] > best_score:
                best_category = category
                best_score = data['score']
        
        
        if best_category is None or best_score == 0:
            best_category = TicketCategory.GENERAL
            confidence = 0.3
            reasoning = "No specific keywords found, using general category"
        else:
           
            total_possible = len(self.keywords[best_category])
            confidence = min(best_score / total_possible, 1.0)
            
            found_words = category_scores[best_category]['keywords']
            reasoning = f"Found {best_score} keywords: {', '.join(found_words)}"
        
        return {
            'category': best_category,
            'confidence': confidence,
            'reasoning': reasoning,
            'score': best_score
        }


def classify_ticket_node(state: Dict) -> Dict:
    """
    Simple function that takes ticket info and returns classification
    This is what gets called by the main system
    """
    try:
        # Get the ticket info from state
        subject = state.get("subject", "")
        description = state.get("description", "")
        
        # Check if we have the required info
        if not subject or not description:
            logger.error("Missing subject or description")
            
            # Get current log and add error message
            processing_log = state.get("processing_log", [])
            processing_log.append("❌ Classification failed: Missing ticket information")
            
            return {
                "classification": TicketCategory.GENERAL.value,
                "processing_log": processing_log
            }
        
        # Create classifier and run classification
        classifier = SimpleTicketClassifier()
        result = classifier.classify_ticket(subject, description)
        
        logger.info(f"Classified as {result['category'].value} with confidence {result['confidence']:.2f}")
        
        # Add results to processing log
        processing_log = state.get("processing_log", [])
        processing_log.append(f"✅ Classified as: {result['category'].value}")
        processing_log.append(f"📊 Confidence: {result['confidence']:.2f}")
        processing_log.append(f"🔍 Reasoning: {result['reasoning']}")
        
        # Return the updated state
        return {
            "classification": result['category'].value,
            "processing_log": processing_log,
            "classification_confidence": result['confidence']
        }
        
    except Exception as e:
        # If something goes wrong, log the error and use GENERAL category
        error_msg = f"Classification error: {str(e)}"
        logger.error(error_msg)
        
        processing_log = state.get("processing_log", [])
        processing_log.append(f"❌ {error_msg}")
        processing_log.append(f"🔄 Using general category as fallback")
        
        return {
            "classification": TicketCategory.GENERAL.value,
            "processing_log": processing_log,
            "classification_confidence": 0.3
        }


# Simple test function
def test_classifier():
    """Test the classifier with some example tickets"""
    
    test_cases = [
        {
            "subject": "Payment Issue",
            "description": "I was charged twice for my subscription this month",
            "expected": "Should be BILLING"
        },
        {
            "subject": "Login Problem", 
            "description": "I can't login to my account with my password",
            "expected": "Should be SECURITY"
        },
        {
            "subject": "App Crash",
            "description": "The app keeps crashing when I try to open it",
            "expected": "Should be TECHNICAL"
        },
        {
            "subject": "General Question",
            "description": "How do I use the dark mode feature?",
            "expected": "Should be GENERAL"
        }
    ]
    
    classifier = SimpleTicketClassifier()
    
    print("🧪 Testing Simple Classifier")
    print("=" * 50)
    
    for i, case in enumerate(test_cases, 1):
        result = classifier.classify_ticket(case["subject"], case["description"])
        
        print(f"\nTest {i}:")
        print(f"Subject: {case['subject']}")
        print(f"Description: {case['description']}")
        print(f"Result: {result['category'].value}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Expected: {case['expected']}")
        print("-" * 30)


if __name__ == "__main__":
    test_classifier()