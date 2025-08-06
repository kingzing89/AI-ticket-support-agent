# src/escalation_logger.py
import csv
import os
from datetime import datetime
from typing import Dict

class EscalationLogger:
    def __init__(self, csv_file: str = "escalation_log.csv"):
        self.csv_file = csv_file
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp',
                    'subject', 
                    'description',
                    'classification',
                    'attempts',
                    'final_draft',
                    'final_feedback',
                    'escalation_reason'
                ])
    
    def log_escalation(self, state: Dict):
        """Log an escalated ticket to CSV"""
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    datetime.now().isoformat(),
                    state.get('subject', ''),
                    state.get('description', ''),
                    state.get('classification', ''),
                    state.get('draft_attempt', 1),
                    state.get('draft_response', ''),
                    state.get('reviewer_feedback', ''),
                    'Max attempts reached'
                ])
            print(f"✅ Escalation logged to {self.csv_file}")
        except Exception as e:
            print(f"❌ Failed to log escalation: {str(e)}")

# Update the escalation node in graph.py to use this
def escalation_node_with_logging(state: Dict) -> dict:
    """Enhanced escalation node with CSV logging"""
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info("Escalating ticket after max attempts reached")
    
    # Log to CSV
    escalation_logger = EscalationLogger()
    escalation_logger.log_escalation(state)
    
    escalation_message = f"""This ticket has been escalated for human review after failing automated processing.

Original Ticket:
Subject: {state['subject']}  
Description: {state['description']}
Classification: {state['classification']}

Attempts Made: {state.get('draft_attempt', 1)}
Failed Draft: {state.get('draft_response', 'No draft generated')}
Final Reviewer Feedback: {state.get('reviewer_feedback', 'No feedback available')}

Please review and respond manually."""
    
    return {
        "escalated": True,
        "max_attempts_reached": True,
        "escalation_message": escalation_message
    }