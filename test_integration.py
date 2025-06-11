#!/usr/bin/env python3
"""
Integration test for frontend-backend communication
Tests all major API endpoints and functionality
"""

import requests
import pandas as pd
import json
import os
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_health_checks():
    """Test all health check endpoints."""
    print("🏥 Testing Health Checks...")
    
    endpoints = [
        "/health/",
        "/data/health/", 
        "/ai/health/",
        "/query/health/",
        "/viz/health/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"   ✅ {endpoint} - OK")
            else:
                print(f"   ❌ {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")

def test_data_upload():
    """Test CSV upload functionality."""
    print("\n📤 Testing Data Upload...")
    
    # Create test CSV
    test_data = {
        'product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones'],
        'price': [999.99, 29.99, 79.99, 299.99, 149.99],
        'category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Audio'],
        'stock': [50, 200, 150, 30, 75]
    }
    
    df = pd.DataFrame(test_data)
    csv_file = 'test_products.csv'
    df.to_csv(csv_file, index=False)
    
    try:
        with open(csv_file, 'rb') as f:
            files = {'file': (csv_file, f, 'text/csv')}
            data = {
                'name': 'Test Products Dataset',
                'description': 'Test dataset for integration testing'
            }
            
            response = requests.post(f"{BASE_URL}/data/upload/", files=files, data=data, timeout=60)
            
            if response.status_code == 201:
                result = response.json()
                print("   ✅ Upload successful!")
                print(f"   📊 Data Source ID: {result.get('data_source', {}).get('id')}")
                return result.get('data_source', {}).get('id')
            else:
                print(f"   ❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return None
    finally:
        if os.path.exists(csv_file):
            os.remove(csv_file)

def test_query_processing(data_source_id):
    """Test natural language query processing."""
    print("\n🤖 Testing Query Processing...")
    
    test_queries = [
        "Show me all products",
        "What's the average price?",
        "Which category has the most products?",
        "Find products under $100"
    ]
    
    for query in test_queries:
        try:
            response = requests.post(f"{BASE_URL}/query/process/", json={
                "query": query,
                "data_source_id": data_source_id,
                "include_sql": True,
                "include_visualization": True
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ '{query}' - {result.get('row_count', 0)} results")
            else:
                print(f"   ❌ '{query}' - {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ '{query}' - Error: {e}")

def test_sql_generation():
    """Test SQL generation from natural language."""
    print("\n🔧 Testing SQL Generation...")
    
    try:
        response = requests.post(f"{BASE_URL}/query/generate-sql/", json={
            "query": "Show me products with price greater than 100"
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ SQL generation successful!")
            print(f"   SQL: {result.get('sql_query', '')[:100]}...")
        else:
            print(f"   ❌ SQL generation failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ SQL generation error: {e}")

def test_visualization_suggestions():
    """Test visualization suggestions."""
    print("\n📊 Testing Visualization Suggestions...")
    
    test_data = [
        {'product': 'Laptop', 'price': 999.99, 'category': 'Electronics'},
        {'product': 'Mouse', 'price': 29.99, 'category': 'Accessories'},
        {'product': 'Keyboard', 'price': 79.99, 'category': 'Accessories'}
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/viz/suggestions/", json={
            "data": test_data
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            suggestions = result.get('suggestions', [])
            print(f"   ✅ Got {len(suggestions)} visualization suggestions")
            for suggestion in suggestions[:3]:
                print(f"   📈 {suggestion.get('title')} - {suggestion.get('suitability')}")
        else:
            print(f"   ❌ Visualization suggestions failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Visualization suggestions error: {e}")

def test_data_sources_api():
    """Test data sources listing."""
    print("\n📋 Testing Data Sources API...")
    
    try:
        response = requests.get(f"{BASE_URL}/data/sources/", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            sources = data.get('results', data) if isinstance(data, dict) else data
            print(f"   ✅ Found {len(sources)} data sources")
            
            for source in sources[:3]:
                print(f"   📊 {source.get('name', 'N/A')} - {source.get('status', 'N/A')}")
        else:
            print(f"   ❌ Data sources API failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Data sources API error: {e}")

def test_ai_chat():
    """Test AI chat functionality."""
    print("\n💬 Testing AI Chat...")
    
    try:
        response = requests.post(f"{BASE_URL}/ai/test-chat/", json={
            "message": "Hello, can you help me analyze data?"
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ AI chat successful!")
            print(f"   🤖 Response: {result.get('ai_response', '')[:100]}...")
        else:
            print(f"   ❌ AI chat failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ AI chat error: {e}")

def main():
    """Run all integration tests."""
    print("🚀 FRONTEND-BACKEND INTEGRATION TEST")
    print("=" * 60)
    
    # Test health checks
    test_health_checks()
    
    # Test data upload and get data source ID
    data_source_id = test_data_upload()
    
    # Test query processing if upload was successful
    if data_source_id:
        test_query_processing(data_source_id)
    
    # Test other endpoints
    test_sql_generation()
    test_visualization_suggestions()
    test_data_sources_api()
    test_ai_chat()
    
    print("\n" + "=" * 60)
    print("🎉 Integration tests completed!")
    print("\n💡 If all tests passed, your frontend-backend integration is working!")

if __name__ == "__main__":
    main()
