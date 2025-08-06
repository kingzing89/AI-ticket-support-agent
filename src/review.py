# src/review.py
import logging
from typing import Dict, Tuple
from .groq_client import GroqClient

class DraftReviewer:
    def __init__(self):
        self.client = GroqClient()
        self.logger = logging.getLogger(__name__)
    
    def review_draft(self, subject: str, description: str, classification: str, 
                    draft_response: str, attempt: int = 1) -> Tuple[bool, str]:
    
        self.logger.info(f"Reviewing draft for {classification} ticket, attempt {attempt}")
        
        # Get category-specific review criteria
        review_prompt = self._build_review_prompt(
            subject, description, classification, draft_response, attempt
        )
        
        system_prompt = self._get_reviewer_system_prompt(classification)
        
        try:
            review_result = self.client.simple_completion(
                prompt=review_prompt,
                system_prompt=system_prompt,
                model="llama3-8b-8192",
                temperature=0.1,  
                max_tokens=300
            )
            
            # Parse the review result
            approved, feedback = self._parse_review_result(review_result)
            
            self.logger.info(f"Review completed: {'APPROVED' if approved else 'REJECTED'}")
            return approved, feedback
            
        except Exception as e:
            self.logger.error(f"Error during review: {str(e)}")
            # Default to rejection with generic feedback on error
            return False, "Unable to complete review due to technical issues. Please revise the response to be more helpful and accurate."
    
    def _get_reviewer_system_prompt(self, classification: str) -> str:
        """Get category-specific reviewer system prompt"""

        base_prompt = """You are an MODERATELY STRICT customer support quality assurance reviewer with VERY HIGH STANDARDS.

STRICT REJECTION CRITERIA (REJECT if ANY are missing):
1. EMPATHY: Must genuinely acknowledge customer frustration with specific empathetic language (not just "I understand")
2. LENGTH: Must be at least 80 words for any non-trivial issue 
3. SPECIFICITY: Must provide at least 2-3 concrete, actionable steps
4. PERSONALIZATION: Must address the customer's specific situation (not generic template responses)
5. COMPLETENESS: Must address ALL parts of the customer's inquiry
6. FOLLOW-UP: Must provide clear next steps or contact information

SPECIAL TESTING RULES:
- For very short/vague tickets (like "Test", "Help"), ALWAYS REJECT 
- If customer request is vague, response must ask for specific details

IMPORTANT: You must respond in this exact format:
DECISION: [APPROVED/REJECTED]
FEEDBACK: [Your specific, detailed feedback about what needs to be improved]"""

        


        category_specific = {
            "billing": """

BILLING-SPECIFIC POLICIES:
- Never guarantee refunds without proper authorization
- Don't provide specific billing amounts or account details
- Always direct complex billing issues to the billing team
- Be clear about billing cycles and processing times
- Don't make promises about waiving fees""",

            "technical": """

TECHNICAL-SPECIFIC POLICIES:
- Provide step-by-step troubleshooting when possible
- Don't make promises about bug fixes or feature timelines
- Always ask for more details if the issue isn't clear
- Suggest escalation to technical team for complex issues
- Include browser/device compatibility information when relevant""",

            "security": """

SECURITY-SPECIFIC POLICIES:
- Take all security concerns seriously
- Never ask for passwords or sensitive information
- Recommend immediate security actions (password change, 2FA)
- Escalate suspicious activity to security team immediately
- Be clear about security timelines and processes""",

            "general": """

GENERAL SUPPORT POLICIES:
- Provide helpful information about our services
- Direct users to appropriate teams when needed
- Be patient with questions and provide clear guidance
- Offer additional help and follow-up options"""
        }
        
        return base_prompt + category_specific.get(classification.lower(), category_specific["general"])
    
    def _build_review_prompt(self, subject: str, description: str, classification: str, 
                           draft_response: str, attempt: int) -> str:
        """Build the review prompt"""
        
        prompt = f"""Please review this customer support response draft:

ORIGINAL TICKET:
Subject: {subject}
Description: {description}
Category: {classification}

DRAFT RESPONSE:
{draft_response}

REVIEW CONTEXT:
- This is attempt #{attempt}
- Please evaluate against all criteria mentioned in your instructions
- Be thorough but constructive in your feedback

Please provide your evaluation in the required format."""

        return prompt
    
    def _parse_review_result(self, review_result: str) -> Tuple[bool, str]:
        """Parse the LLM review result into approval status and feedback"""
        
        lines = review_result.strip().split('\n')
        decision_line = ""
        feedback_lines = []
        
        found_decision = False
        found_feedback = False
        
        for line in lines:
            line = line.strip()
            if line.startswith("DECISION:"):
                decision_line = line.replace("DECISION:", "").strip()
                found_decision = True
            elif line.startswith("FEEDBACK:"):
                feedback_lines.append(line.replace("FEEDBACK:", "").strip())
                found_feedback = True
            elif found_feedback:
                # Continue collecting feedback lines
                feedback_lines.append(line)
        
        # Determine approval
        approved = False
        if found_decision:
            approved = "APPROVED" in decision_line.upper()
        
        # Get feedback
        feedback = " ".join(feedback_lines).strip()
        if not feedback:
            if approved:
                feedback = "Response meets all quality standards and policies."
            else:
                feedback = "Response needs improvement. Please revise for better accuracy and helpfulness."
        
        return approved, feedback


def review_node(state: Dict) -> Dict:
    """
    LangGraph node function for draft review
    """
    reviewer = DraftReviewer()
    
    # Get current attempt number
    attempt = state.get('draft_attempt', 1)
    
    # Review the draft
    approved, feedback = reviewer.review_draft(
        subject=state['subject'],
        description=state['description'],
        classification=state['classification'],
        draft_response=state['draft_response'],
        attempt=attempt
    )
    
    return {
        "review_passed": approved,
        "reviewer_feedback": feedback,
        "draft_attempt": attempt
    }


# Test function
def test_draft_review():
    """Test the draft review functionality"""
    reviewer = DraftReviewer()
    
    # Test case 1: Good response
    print("=== Test 1: Good Response ===")
    approved, feedback = reviewer.review_draft(
        subject="Password reset not working",
        description="I can't login and the password reset email isn't coming",
        classification="technical",
        draft_response="""Thank you for contacting us about your login issue. I understand how frustrating this must be.

Here are the steps to resolve this:

1. First, please check your spam/junk folder for the password reset email
2. If it's not there, please wait 5-10 minutes as emails can sometimes be delayed
3. Try using the password reset link again, making sure to enter the exact email address associated with your account
4. If you're still not receiving the email after 15 minutes, please contact our technical support team who can assist you further

For future reference, you can also enable two-factor authentication in your account settings for added security.

Is there anything else I can help you with today?"""
    )
    
    print(f"Approved: {approved}")
    print(f"Feedback: {feedback}")
    print()
    
    # Test case 2: Poor response
    print("=== Test 2: Poor Response ===")
    approved, feedback = reviewer.review_draft(
        subject="Need refund for billing error", 
        description="I was charged twice this month",
        classification="billing",
        draft_response="Sure, I'll process your refund right away. You should see it in your account tomorrow."
    )
    
    print(f"Approved: {approved}")
    print(f"Feedback: {feedback}")
    print()

if __name__ == "__main__":
    test_draft_review()