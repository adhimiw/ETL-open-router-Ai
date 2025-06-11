#!/usr/bin/env python3
"""
Test the enhanced query processing with real data access
"""

import requests
import pandas as pd
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_enhanced_queries():
    """Test enhanced query processing with actual data analysis."""
    print("🧪 Testing Enhanced Query Processing...")
    
    # First, upload test data
    test_data = {
        'product': ['Laptop Pro', 'Gaming Mouse', 'Mechanical Keyboard', '4K Monitor', 'Wireless Headphones', 
                   'Tablet', 'Smartphone', 'Webcam', 'Speakers', 'External Drive'],
        'price': [1299.99, 79.99, 149.99, 399.99, 199.99, 
                 599.99, 899.99, 129.99, 89.99, 119.99],
        'category': ['Computers', 'Accessories', 'Accessories', 'Monitors', 'Audio',
                    'Tablets', 'Phones', 'Accessories', 'Audio', 'Storage'],
        'total_amount': [1299.99, 79.99, 149.99, 399.99, 199.99, 
                        599.99, 899.99, 129.99, 89.99, 119.99],
        'stock': [25, 150, 75, 40, 60, 30, 45, 80, 90, 100],
        'rating': [4.8, 4.5, 4.7, 4.6, 4.4, 4.3, 4.9, 4.2, 4.1, 4.0]
    }
    
    df = pd.DataFrame(test_data)
    csv_file = 'enhanced_test_data.csv'
    df.to_csv(csv_file, index=False)
    
    # Upload the data
    try:
        with open(csv_file, 'rb') as f:
            files = {'file': (csv_file, f, 'text/csv')}
            data = {
                'name': 'Enhanced Test Dataset',
                'description': 'Test dataset with value columns for enhanced query testing'
            }
            
            response = requests.post(f"{BASE_URL}/data/upload/", files=files, data=data, timeout=60)
            
            if response.status_code == 201:
                result = response.json()
                data_source_id = result.get('data_source', {}).get('id')
                print(f"✅ Data uploaded successfully! ID: {data_source_id}")
            else:
                print(f"❌ Upload failed: {response.status_code}")
                return
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    finally:
        import os
        if os.path.exists(csv_file):
            os.remove(csv_file)
    
    # Test enhanced queries
    test_queries = [
        "What are the top 5 products by price?",
        "Show me the top 3 records by total amount",
        "What's the average price of all products?",
        "Give me a summary of the data",
        "Group products by category"
    ]
    
    print(f"\n🔍 Testing {len(test_queries)} enhanced queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        try:
            response = requests.post(f"{BASE_URL}/query/process/", json={
                "query": query,
                "data_source_id": data_source_id,
                "include_sql": True,
                "include_visualization": True
            }, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('row_count', 0)} results")
                
                # Show AI response (first 200 chars)
                ai_response = result.get('ai_response', '')
                print(f"   🤖 AI Response: {ai_response[:200]}...")
                
                # Show query analysis if available
                query_analysis = result.get('query_analysis')
                if query_analysis:
                    print(f"   📊 Analysis: {query_analysis[:150]}...")
                
                # Show first result if available
                results = result.get('results', [])
                if results:
                    first_result = results[0]
                    print(f"   📋 First Result: {first_result}")
                    
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 Enhanced query testing completed!")

if __name__ == "__main__":
    test_enhanced_queries()
