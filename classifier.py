"""
Classification Node for Support Ticket Agent - WORKING VERSION
This node classifies tickets into predefined categories using multiple approaches
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from src.models import TicketCategory  # Keep this for the enum

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of ticket classification"""
    category: TicketCategory
    confidence: float
    reasoning: str
    keywords_found: List[str]
    fallback_used: bool = False


class TicketClassifier:
    """
    Multi-approach ticket classifier that combines keyword-based and pattern-based classification
    Designed to be reliable even with vague or multi-intent descriptions
    """
    
    def __init__(self):
        # Define category-specific keywords and patterns
        self.category_keywords = {
            TicketCategory.BILLING: {
                'primary': ['billing', 'payment', 'charge', 'invoice', 'refund', 'subscription', 'plan', 'price', 'cost', 'money', 'credit card', 'debit'],
                'secondary': ['account balance', 'upgrade', 'downgrade', 'cancel', 'renewal', 'receipt', 'transaction', 'fee', 'discount', 'promo'],
                'patterns': [r'charged?\s+(?:me|twice|wrong)', r'billing\s+(?:question|issue|problem)', r'refund\s+(?:request|please)', r'\$\d+']
            },
            TicketCategory.TECHNICAL: {
                'primary': ['error', 'bug', 'crash', 'broken', 'not working', 'malfunction', 'glitch', 'issue', 'problem', 'fail'],
                'secondary': ['website', 'app', 'mobile', 'desktop', 'browser', 'loading', 'slow', 'timeout', 'server', 'api', 'feature'],
                'patterns': [r'error\s+(?:code|message)', r'(?:app|website)\s+(?:crash|down|broken)', r'can\'t\s+(?:access|load|open)', r'\d{3}\s+error']
            },
            TicketCategory.SECURITY: {
                'primary': ['password', 'login', 'access', 'account', 'security', 'hacked', 'compromised', 'suspicious', 'unauthorized'],
                'secondary': ['two factor', '2fa', 'verification', 'reset', 'locked out', 'breach', 'phishing', 'spam', 'fraud'],
                'patterns': [r'can\'t\s+(?:login|log\s+in|access)', r'password\s+(?:reset|recovery|forgot)', r'account\s+(?:locked|compromised|hacked)']
            },
            TicketCategory.GENERAL: {
                'primary': ['question', 'help', 'how to', 'information', 'support', 'inquiry', 'request', 'feature'],
                'secondary': ['documentation', 'tutorial', 'guide', 'training', 'demo', 'consultation', 'advice', 'recommendation'],
                'patterns': [r'how\s+(?:do\s+i|to|can)', r'feature\s+request', r'general\s+(?:question|inquiry)']
            }
        }
        
        # Priority order for multi-category matches
        self.category_priority = [
            TicketCategory.SECURITY,    # Highest priority
            TicketCategory.BILLING,
            TicketCategory.TECHNICAL,
            TicketCategory.GENERAL      # Lowest priority (catch-all)
        ]
    
    def classify_ticket(self, subject: str, description: str) -> ClassificationResult:
        """
        Classify a ticket using multiple approaches for reliability
        
        Args:
            subject: Ticket subject line
            description: Ticket description
            
        Returns:
            ClassificationResult with category and confidence
        """
        # Combine subject and description for analysis
        full_text = f"{subject} {description}".lower()
        
        # Run all classification approaches
        keyword_result = self._classify_by_keywords(full_text)
        pattern_result = self._classify_by_patterns(full_text)
        heuristic_result = self._classify_by_heuristics(subject, description)
        
        # Combine results with weighted scoring
        final_result = self._combine_classification_results([
            keyword_result,
            pattern_result,
            heuristic_result
        ])
        
        logger.info(f"Classified ticket as {final_result.category.value} with confidence {final_result.confidence:.2f}")
        
        return final_result
    
    def _classify_by_keywords(self, text: str) -> Dict[TicketCategory, float]:
        """Classify based on keyword matching"""
        scores = {category: 0.0 for category in TicketCategory}
        
        for category, keywords in self.category_keywords.items():
            # Primary keywords get higher weight
            for keyword in keywords['primary']:
                if keyword in text:
                    scores[category] += 2.0
            
            # Secondary keywords get lower weight
            for keyword in keywords['secondary']:
                if keyword in text:
                    scores[category] += 1.0
        
        return scores
    
    def _classify_by_patterns(self, text: str) -> Dict[TicketCategory, float]:
        """Classify based on regex pattern matching"""
        scores = {category: 0.0 for category in TicketCategory}
        
        for category, keywords in self.category_keywords.items():
            for pattern in keywords.get('patterns', []):
                if re.search(pattern, text, re.IGNORECASE):
                    scores[category] += 3.0  # Patterns get high weight
        
        return scores
    
    def _classify_by_heuristics(self, subject: str, description: str) -> Dict[TicketCategory, float]:
        """Classify using domain-specific heuristics"""
        scores = {category: 0.0 for category in TicketCategory}
        
        subject_lower = subject.lower()
        description_lower = description.lower()
        
        # Heuristic 1: Subject line indicators
        if any(word in subject_lower for word in ['billing', 'payment', 'charge']):
            scores[TicketCategory.BILLING] += 2.0
        
        if any(word in subject_lower for word in ['login', 'password', 'access']):
            scores[TicketCategory.SECURITY] += 2.0
        
        if any(word in subject_lower for word in ['error', 'bug', 'crash', 'broken']):
            scores[TicketCategory.TECHNICAL] += 2.0
        
        # Heuristic 2: Urgency indicators often correlate with technical issues
        urgency_words = ['urgent', 'asap', 'immediately', 'critical', 'emergency']
        if any(word in description_lower for word in urgency_words):
            scores[TicketCategory.TECHNICAL] += 1.0
            scores[TicketCategory.SECURITY] += 1.0
        
        # Heuristic 3: Question patterns often indicate general inquiries
        question_patterns = ['how do i', 'how can i', 'how to', 'what is', 'where can', 'when will']
        if any(pattern in description_lower for pattern in question_patterns):
            scores[TicketCategory.GENERAL] += 1.5
        
        # Heuristic 4: Currency symbols or numbers often indicate billing
        if re.search(r'[\$£€¥]\d+|\d+\.\d{2}', description):
            scores[TicketCategory.BILLING] += 2.0
        
        # Heuristic 5: Error codes indicate technical issues
        if re.search(r'error\s*(?:code\s*)?\d+|\d{3}\s*error', description_lower):
            scores[TicketCategory.TECHNICAL] += 2.5
        
        return scores
    
    def _combine_classification_results(self, results: List[Dict[TicketCategory, float]]) -> ClassificationResult:
        """Combine multiple classification results into final decision"""
        
        # Aggregate scores from all methods
        combined_scores = {category: 0.0 for category in TicketCategory}
        
        for result in results:
            for category, score in result.items():
                combined_scores[category] += score
        
        # Find the category with highest score
        if max(combined_scores.values()) == 0:
            # No matches found, default to GENERAL
            return ClassificationResult(
                category=TicketCategory.GENERAL,
                confidence=0.3,
                reasoning="No clear category indicators found, defaulting to general",
                keywords_found=[],
                fallback_used=True
            )
        
        # Get top category
        top_category = max(combined_scores, key=combined_scores.get)
        top_score = combined_scores[top_category]
        
        # Calculate confidence (normalize score)
        total_score = sum(combined_scores.values())
        confidence = min(top_score / max(total_score, 1.0), 1.0)
        
        # If confidence is too low and there's a tie, use priority order
        if confidence < 0.4:
            # Check for ties within confidence threshold
            threshold = top_score * 0.8
            candidates = [cat for cat, score in combined_scores.items() if score >= threshold]
            
            if len(candidates) > 1:
                # Use priority order to break ties
                for priority_cat in self.category_priority:
                    if priority_cat in candidates:
                        top_category = priority_cat
                        break
        
        # Generate reasoning and keywords
        reasoning_parts = []
        keywords_found = []
        
        for category, score in combined_scores.items():
            if score > 0 and category == top_category:
                reasoning_parts.append(f"{category.value} indicators (score: {score:.1f})")
        
        reasoning = f"Classified as {top_category.value} based on: {', '.join(reasoning_parts)}"
        
        return ClassificationResult(
            category=top_category,
            confidence=confidence,
            reasoning=reasoning,
            keywords_found=keywords_found,
            fallback_used=False
        )


def classify_ticket_node(state: Dict) -> Dict:
    """
    LangGraph node function for ticket classification.
    FIXED VERSION - Properly handles processing_log and state management
    
    Args:
        state: Current state dict containing subject and description
        
    Returns:
        Updated state dict with classification and updated processing_log
    """
    try:
        # Get subject and description from state
        subject = state.get("subject", "")
        description = state.get("description", "")
        
        if not subject or not description:
            logger.error("Missing subject or description in state")
            
            # Get existing processing log and add error
            processing_log = state.get("processing_log", [])
            processing_log.append("❌ Classification failed: Missing subject or description")
            
            return {
                "classification": TicketCategory.GENERAL.value,
                "processing_log": processing_log
            }
        
        # Initialize classifier
        classifier = TicketClassifier()
        
        # Perform classification
        classification_result = classifier.classify_ticket(subject, description)
        
        logger.info(f"Classified ticket as {classification_result.category.value} with confidence {classification_result.confidence:.2f}")
        
        # Get existing processing log or create new one
        processing_log = state.get("processing_log", [])
        
        # Add classification results to processing log
        processing_log.append(f"✅ Classification completed: {classification_result.category.value}")
        processing_log.append(f"📊 Confidence: {classification_result.confidence:.2f}")
        processing_log.append(f"🧠 Reasoning: {classification_result.reasoning}")
        
        if classification_result.fallback_used:
            processing_log.append("⚠️ Fallback classification used - consider manual review")
        
        # Create classification metadata
        classification_metadata = {
            "confidence": classification_result.confidence,
            "reasoning": classification_result.reasoning,
            "keywords_found": classification_result.keywords_found,
            "fallback_used": classification_result.fallback_used
        }
        
        # Return updated state dict - THIS IS THE KEY FIX
        return {
            "classification": classification_result.category.value,
            "processing_log": processing_log,
            "classification_metadata": classification_metadata
        }
        
    except Exception as e:
        error_msg = f"Classification error: {str(e)}"
        logger.error(error_msg)
        
        # Get existing processing log and add error
        processing_log = state.get("processing_log", [])
        processing_log.append(f"❌ {error_msg}")
        processing_log.append(f"🔄 Fallback: classified as {TicketCategory.GENERAL.value} due to error")
        
        # Fallback to GENERAL category on error
        return {
            "classification": TicketCategory.GENERAL.value,
            "processing_log": processing_log
        }


def get_classification_confidence(state: Dict) -> float:
    """Helper function to get classification confidence from state"""
    metadata = state.get("classification_metadata", {})
    return metadata.get("confidence", 0.0)


def is_classification_reliable(state: Dict, threshold: float = 0.6) -> bool:
    """Helper function to check if classification is reliable enough"""
    confidence = get_classification_confidence(state)
    fallback_used = state.get("classification_metadata", {}).get("fallback_used", False)
    
    return confidence >= threshold and not fallback_used


# Test function to verify the fix
def test_classify_node():
    """Test the classify_ticket_node function to ensure it works properly"""
    
    test_state = {
        "subject": "Login issue", 
        "description": "I am getting 404 when logging in with the correct password and username",
        "processing_log": ["Initial ticket received"]
    }
    
    print("🧪 Testing classify_ticket_node function...")
    print(f"Input state: {test_state}")
    
    result = classify_ticket_node(test_state)
    
    print(f"\n✅ Result: {result}")
    print(f"\n📋 Processing Log:")
    for log_entry in result.get("processing_log", []):
        print(f"  • {log_entry}")
    
    return result


# Test cases for the classifier
def create_test_classification_cases():
    """Create test cases to validate classifier reliability"""
    return [
        # Clear billing cases
        {
            "subject": "Double charged for subscription",
            "description": "I was charged $29.99 twice for my monthly subscription. Can you please refund one of the charges?",
            "expected": TicketCategory.BILLING
        },
        {
            "subject": "Payment failed",
            "description": "My credit card payment failed but I need to update my billing information",
            "expected": TicketCategory.BILLING
        },
        
        # Clear technical cases
        {
            "subject": "App crashes on startup",
            "description": "The mobile app crashes every time I try to open it. Error code 500. This started after the latest update.",
            "expected": TicketCategory.TECHNICAL
        },
        {
            "subject": "Website not loading",
            "description": "I can't access the website. It shows a server error and won't load any pages.",
            "expected": TicketCategory.TECHNICAL
        },
        
        # Clear security cases
        {
            "subject": "Can't login to my account",
            "description": "I can't log into my account. I'm sure my password is correct but it says invalid credentials.",
            "expected": TicketCategory.SECURITY
        },
        {
            "subject": "Suspicious activity alert",
            "description": "I received an email about suspicious login activity from Russia. I need to secure my account immediately.",
            "expected": TicketCategory.SECURITY
        },
        
        # Clear general cases
        {
            "subject": "How to use dark mode?",
            "description": "I would like to know how to enable dark mode in the application. Is this feature available?",
            "expected": TicketCategory.GENERAL
        },
        {
            "subject": "Feature request",
            "description": "I would like to request a new feature for bulk data export. When will this be available?",
            "expected": TicketCategory.GENERAL
        }
    ]


if __name__ == "__main__":
    # First test the node function
    print("🔧 Testing Node Function Fix...")
    test_result = test_classify_node()
    
    if test_result and "classification" in test_result and "processing_log" in test_result:
        print("✅ Node function test PASSED!")
    else:
        print("❌ Node function test FAILED!")
        exit(1)
    
    print("\n" + "="*60)
    
    # Then test the full classifier
    print("🧪 Testing Full Classification Logic...")
    print("=" * 60)
    
    classifier = TicketClassifier()
    test_cases = create_test_classification_cases()
    
    correct_predictions = 0
    total_predictions = 0
    
    for i, case in enumerate(test_cases, 1):
        result = classifier.classify_ticket(case["subject"], case["description"])
        
        print(f"\n--- Test Case {i} ---")
        print(f"Subject: {case['subject']}")
        print(f"Description: {case['description'][:100]}...")
        print(f"Expected: {case['expected'].value}")
        print(f"Predicted: {result.category.value}")
        print(f"Confidence: {result.confidence:.2f}")
        
        is_correct = result.category == case["expected"]
        status = "✅ CORRECT" if is_correct else "❌ INCORRECT"
        print(f"Result: {status}")
        
        if is_correct:
            correct_predictions += 1
        total_predictions += 1
    
    accuracy = correct_predictions / total_predictions
    print(f"\n📊 Overall Accuracy: {accuracy:.2%} ({correct_predictions}/{total_predictions})")
    print("\n🏁 Classification testing completed!")
    print("\n🚀 The classifier is ready for use in main.py!") 