# src/draft_generation.py
import os
import logging
from typing import Dict
from .groq_client import GroqClient

class DraftGenerator:
    def __init__(self):
        self.client = GroqClient()
        self.logger = logging.getLogger(__name__)
    
    def generate_draft(self, subject: str, description: str, classification: str, 
                      formatted_context: str, reviewer_feedback: str = None, 
                      attempt: int = 1) -> str:
        """
        Generate a draft response based on the ticket and retrieved context
        
        Args:
            subject: Ticket subject
            description: Ticket description  
            classification: Ticket category
            formatted_context: Retrieved documentation
            reviewer_feedback: Feedback from previous review (for retries)
            attempt: Current attempt number
            
        Returns:
            Draft response string
        """
        self.logger.info(f"Generating draft for {classification} ticket, attempt {attempt}")
        
        # Build the system prompt based on category
        system_prompt = self._get_category_system_prompt(classification)
        
        # Build the user prompt
        user_prompt = self._build_user_prompt(
            subject, description, formatted_context, reviewer_feedback, attempt
        )
        
        try:
            # Use the Groq client for completion
            draft = self.client.simple_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model="llama3-8b-8192",  # Fast and capable model
                temperature=0.3,
                max_tokens=500
            )
            
            self.logger.info("Draft generated successfully with Groq")
            return draft
            
        except Exception as e:
            self.logger.error(f"Error generating draft with Groq: {str(e)}")
            return self._get_fallback_response(classification)
    
    def _get_category_system_prompt(self, classification: str) -> str:
        """Get category-specific system prompts"""
        
        base_prompt = """You are a professional customer support agent. Your goal is to provide helpful, accurate, and empathetic responses to customer inquiries.

IMPORTANT GUIDELINES:
- Be friendly and professional
- Provide clear, actionable steps when possible
- Don't make promises you can't keep
- If you need more information, ask for it
- Keep responses concise but thorough
- Always acknowledge the customer's concern"""

        category_prompts = {
            "billing": base_prompt + """

BILLING-SPECIFIC RULES:
- For refund requests, explain the process but don't guarantee approval
- Direct complex billing issues to the billing team
- Always mention checking account settings for payment updates
- Be clear about billing cycles and timing""",

            "technical": base_prompt + """

TECHNICAL-SPECIFIC RULES:
- Provide step-by-step troubleshooting when possible
- Suggest common solutions first (cache clearing, updates, restarts)
- Ask for specific error messages or browser/device info if needed
- Offer to escalate to technical team for complex issues""",

            "security": base_prompt + """

SECURITY-SPECIFIC RULES:
- Take all security concerns seriously
- Recommend immediate action for account safety
- Don't ask for sensitive information in responses
- Emphasize the importance of strong passwords and 2FA
- Direct urgent security issues to the security team""",

            "general": base_prompt + """

GENERAL SUPPORT RULES:
- Provide helpful information about our services
- Direct users to appropriate resources or teams
- Be patient with general questions
- Offer additional help if needed"""
        }
        
        return category_prompts.get(classification.lower(), base_prompt)
    
    def _build_user_prompt(self, subject: str, description: str, formatted_context: str, 
                          reviewer_feedback: str = None, attempt: int = 1) -> str:
        """Build the user prompt with ticket details and context"""
        
        prompt = f"""Please draft a response to this customer support ticket:

TICKET DETAILS:
Subject: {subject}
Description: {description}

AVAILABLE DOCUMENTATION:
{formatted_context}"""

        # Add reviewer feedback for retries
        if reviewer_feedback and attempt > 1:
            prompt += f"""

PREVIOUS ATTEMPT FEEDBACK:
The previous response was rejected with this feedback: {reviewer_feedback}
Please address these concerns in your new response."""

        prompt += """

Please write a helpful response that:
1. Acknowledges the customer's issue
2. Uses the provided documentation to give accurate information
3. Provides clear next steps or solutions
4. Maintains a professional and empathetic tone

RESPONSE:"""

        return prompt
    
    def _get_fallback_response(self, classification: str) -> str:
        """Provide fallback response if API fails"""
        fallback_responses = {
            "billing": "Thank you for contacting us about your billing inquiry. I understand your concern and want to help resolve this for you. Please allow me some time to review your account details, and I'll get back to you within 24 hours with a comprehensive response. If this is urgent, please contact our billing support team directly.",
            
            "technical": "Thank you for reaching out about this technical issue. I understand how frustrating this can be. While I gather more information to provide you with the best solution, please try these quick steps: clear your browser cache, ensure you're using the latest version of the application, and restart your device. I'll follow up with more specific guidance shortly.",
            
            "security": "Thank you for bringing this security concern to our attention. Your account security is our top priority. As a precautionary measure, please change your password immediately if you haven't already done so. I'm escalating this to our security team who will review your account and contact you within 2 hours.",
            
            "general": "Thank you for contacting our support team. I understand you need assistance, and I'm here to help. I'm currently reviewing your inquiry to provide you with the most accurate information. I'll respond with detailed guidance within 24 hours. If you have any urgent concerns, please don't hesitate to reach out again."
        }
        
        return fallback_responses.get(classification.lower(), fallback_responses["general"])


def draft_generation_node(state: Dict) -> Dict:
    """
    LangGraph node function for draft generation
    """
    generator = DraftGenerator()
    
    # Generate the draft response
    draft = generator.generate_draft(
        subject=state['subject'],
        description=state['description'],
        classification=state['classification'],
        formatted_context=state['formatted_context'],
        reviewer_feedback=state.get('reviewer_feedback'),
        attempt=state.get('retrieval_attempt', 1)
    )
    
    return {
        "draft_response": draft
    }


# Test function
def test_draft_generation():
    """Test the draft generation functionality"""
    generator = DraftGenerator()
    
    # Test case
    test_context = """Relevant Documentation:

1. **Login Issues**
   For login problems, first try clearing your browser cache and cookies. If that doesn't work, try resetting your password. Make sure you're using the correct email address associated with your account.

2. **Password Reset**
   To reset your password, click the 'Forgot Password' link on the login page. You'll receive an email with reset instructions. The reset link expires after 24 hours for security."""
    
    draft = generator.generate_draft(
        subject="Can't login to my account",
        description="I'm having trouble logging in. I tried my password multiple times but it's not working.",
        classification="technical",
        formatted_context=test_context
    )
    
    print("=== Generated Draft ===")
    print(draft)
    print("="*50)

if __name__ == "__main__":
    test_draft_generation()