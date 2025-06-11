#!/usr/bin/env python3
"""
Direct test of OpenRouter API integration without Django.
"""

import openai
import os
import sys

def test_openrouter_direct():
    """Test OpenRouter API directly."""
    
    # Set up OpenAI client for OpenRouter
    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )
    
    try:
        print("Testing OpenRouter API directly...")
        print("-" * 50)
        
        # Test message
        messages = [
            {
                "role": "system", 
                "content": "You are a helpful AI assistant for an ETL (Extract, Transform, Load) platform. Be concise and helpful."
            },
            {
                "role": "user", 
                "content": "Hello! Can you tell me what you are and how you can help with data analysis?"
            }
        ]
        
        # Make API call
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            extra_headers={
                "HTTP-Referer": "https://eetl-ai-platform.com",
                "X-Title": "EETL AI Platform",
            }
        )
        
        print("✅ SUCCESS!")
        print(f"Model: {response.model}")
        print(f"Tokens Used: {response.usage.total_tokens}")
        print(f"Finish Reason: {response.choices[0].finish_reason}")
        print("-" * 50)
        print("AI Response:")
        print(response.choices[0].message.content)
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openrouter_direct()
