#!/usr/bin/env python3
"""
Comprehensive test script for AI chat integration.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_start_conversation():
    """Test starting a new conversation."""
    print("\n🔍 Testing conversation creation...")
    try:
        payload = {
            "title": "Test Conversation",
            "data_source_id": "test_source_123"
        }
        
        response = requests.post(
            f"{BASE_URL}/ai/conversations/", 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Conversation created successfully")
            print(f"   Conversation ID: {data.get('id')}")
            print(f"   Title: {data.get('title')}")
            return data.get('id')
        else:
            print(f"❌ Conversation creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Conversation creation error: {e}")
        return None

def test_send_message(conversation_id):
    """Test sending a message to a conversation."""
    print(f"\n🔍 Testing message sending to conversation {conversation_id}...")
    try:
        payload = {
            "content": "Hello! Can you help me analyze my sales data?",
            "role": "user"
        }
        
        response = requests.post(
            f"{BASE_URL}/ai/conversations/{conversation_id}/messages/", 
            json=payload, 
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Message sent successfully")
            print(f"   User message: {data.get('user_message', {}).get('content', 'N/A')}")
            print(f"   AI response: {data.get('ai_response', {}).get('content', 'N/A')[:100]}...")
            print(f"   Model used: {data.get('ai_response', {}).get('model', 'N/A')}")
            print(f"   Tokens used: {data.get('ai_response', {}).get('tokens_used', 'N/A')}")
            return True
        else:
            print(f"❌ Message sending failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Message sending error: {e}")
        return False

def test_query_processing():
    """Test the natural language query processing."""
    print("\n🔍 Testing query processing...")
    try:
        payload = {
            "query": "Show me the top 10 customers by revenue",
            "data_source_id": "test_source_123",
            "include_sql": True,
            "include_visualization": True
        }
        
        response = requests.post(
            f"{BASE_URL}/query/process/", 
            json=payload, 
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Query processed successfully")
            print(f"   Query: {data.get('query')}")
            print(f"   AI Response: {data.get('ai_response', '')[:100]}...")
            print(f"   Results count: {data.get('row_count', 0)}")
            print(f"   Execution time: {data.get('execution_time', 0):.2f}ms")
            print(f"   Model used: {data.get('model', 'N/A')}")
            print(f"   SQL generated: {data.get('sql_query', 'N/A')[:50]}...")
            return True
        else:
            print(f"❌ Query processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query processing error: {e}")
        return False

def test_ai_chat_endpoint():
    """Test the simple AI chat endpoint."""
    print("\n🔍 Testing simple AI chat endpoint...")
    try:
        payload = {
            "message": "What can you help me with regarding data analysis?"
        }
        
        response = requests.post(
            f"{BASE_URL}/ai/test-chat/", 
            json=payload, 
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ AI chat test successful")
            print(f"   AI Response: {data.get('ai_response', '')[:100]}...")
            print(f"   Model used: {data.get('model', 'N/A')}")
            print(f"   Tokens used: {data.get('tokens_used', 'N/A')}")
            print(f"   Processing time: {data.get('processing_time', 0):.2f}s")
            return True
        else:
            print(f"❌ AI chat test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI chat test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting AI Chat Integration Tests")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("\n❌ Health check failed. Make sure the Django server is running.")
        return
    
    # Test simple AI chat endpoint
    test_ai_chat_endpoint()
    
    # Test conversation flow
    conversation_id = test_start_conversation()
    if conversation_id:
        test_send_message(conversation_id)
    
    # Test query processing
    test_query_processing()
    
    print("\n" + "=" * 50)
    print("🎉 AI Chat Integration Tests Complete!")
    print("\nIf all tests passed, your AI chat is working correctly!")

if __name__ == "__main__":
    main()
