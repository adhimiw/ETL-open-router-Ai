#!/usr/bin/env python3
"""
Test the NaN fix for query processing
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_nan_fix():
    """Test that NaN values don't cause JSON serialization errors."""
    print("🧪 Testing NaN Fix...")
    
    # Test with a known working data source
    data_source_id = "cbe7dbd5-6fd6-4885-b28a-5fa9e0e853c5"  # Enhanced Test Dataset
    
    test_queries = [
        "What are the top 3 products by price?",
        "Show me the average price",
        "Give me a summary of the data"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        
        try:
            response = requests.post(f"{BASE_URL}/query/process/", json={
                "query": query,
                "data_source_id": data_source_id
            }, timeout=45)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   ✅ Success: {result.get('row_count', 0)} results")
                    print(f"   🤖 AI Response: {result.get('ai_response', '')[:100]}...")
                    
                    # Check if results contain any problematic values
                    results = result.get('results', [])
                    if results:
                        print(f"   📊 First Result: {results[0]}")
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON Decode Error: {e}")
                    print(f"   Raw Response: {response.text[:200]}...")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Error Text: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout - Query took too long")
        except Exception as e:
            print(f"   ❌ Request Error: {e}")
    
    print(f"\n🎉 NaN fix testing completed!")

if __name__ == "__main__":
    test_nan_fix()
