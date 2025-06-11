#!/usr/bin/env python3
"""
Simple test script to verify OpenRouter AI chat integration.
"""

import requests
import json

def test_ai_chat():
    """Test the AI chat endpoint."""
    
    # Test endpoint URL
    url = "http://127.0.0.1:8000/api/ai/test-chat/"
    
    # Test message
    test_message = "Hello! Can you tell me what you are and how you can help with data analysis?"
    
    # Request payload
    payload = {
        "message": test_message
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing AI Chat Integration...")
        print(f"Sending message: {test_message}")
        print("-" * 50)
        
        # Make the request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(f"Status: {data.get('status')}")
            print(f"Model: {data.get('model')}")
            print(f"Tokens Used: {data.get('tokens_used')}")
            print(f"Processing Time: {data.get('processing_time'):.2f}s")
            print("-" * 50)
            print("AI Response:")
            print(data.get('ai_response'))
            print("-" * 50)
            
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_ai_chat()
