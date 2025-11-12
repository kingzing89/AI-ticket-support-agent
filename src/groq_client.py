# src/groq_client.py
import os
import requests
import json
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class GroqClient:
    """Simple client for Groq API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required. Set it as environment variable or pass it directly.")
    
    def chat_completion(self, messages: List[Dict], model: str = "llama-3.1-8b-instant", 
                       temperature: float = 0.7, max_tokens: int = 1024,
                       stream: bool = False) -> Dict:
        """
        Create a chat completion using Groq
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (default: llama3-8b-8192)
                   Available models: llama3-8b-8192, llama3-70b-8192, mixtral-8x7b-32768, gemma-7b-it
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Response dict from the API
        """
        payload = {
            "messages": messages,
            "model": model,
            "stream": stream,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Groq API error: {response.status_code}"
                try:
                    error_detail = response.json()
                    if 'error' in error_detail:
                        error_msg += f" - {error_detail['error'].get('message', 'Unknown error')}"
                except:
                    error_msg += f" - {response.text}"
                
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def simple_completion(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """
        Simple completion method that returns just the text response
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional arguments for chat_completion
            
        Returns:
            Generated text response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.chat_completion(messages, **kwargs)
        return response['choices'][0]['message']['content'].strip()


# Test function
def test_groq_client():
    """Test the Groq client"""
    try:
        client = GroqClient()
        
        # Simple test
        response = client.simple_completion(
            prompt="What is the capital of France? Answer in one sentence.",
            system_prompt="You are a helpful assistant.",
            model="llama3-8b-8192",
            temperature=0.3,
            max_tokens=100
        )
        
        print("=== Groq Test Response ===")
        print(response)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"Groq client test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_groq_client()