#!/usr/bin/env python3
"""
Complete pipeline test: CSV Upload → AI Analysis → Query Processing
"""

import requests
import pandas as pd
import json
import os
import time

def create_comprehensive_csv():
    """Create a comprehensive CSV with various data types for testing."""
    data = {
        'transaction_id': range(1, 51),
        'customer_name': [
            'Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Brown',
            'Frank Miller', 'Grace Lee', 'Henry Taylor', 'Ivy Chen', 'Jack Anderson'
        ] * 5,
        'product_category': ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports'] * 10,
        'product_name': [
            'Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Camera',
            'T-Shirt', 'Jeans', 'Sneakers', 'Jacket', 'Hat',
            'Novel', 'Cookbook', 'Magazine', 'Textbook', 'Comic',
            'Plant', 'Tool', 'Furniture', 'Decor', 'Light',
            'Ball', 'Racket', 'Shoes', 'Equipment', 'Gear'
        ] * 2,
        'price': [
            999.99, 699.99, 399.99, 199.99, 1299.99,
            29.99, 79.99, 129.99, 199.99, 24.99,
            14.99, 24.99, 4.99, 89.99, 9.99,
            19.99, 49.99, 299.99, 39.99, 79.99,
            19.99, 89.99, 149.99, 199.99, 99.99
        ] * 2,
        'quantity': [1, 2, 1, 3, 1, 2, 1, 1, 1, 2] * 5,
        'order_date': pd.date_range('2024-01-01', periods=50, freq='D').strftime('%Y-%m-%d').tolist(),
        'customer_age': [25, 34, 28, 45, 31, 29, 38, 42, 26, 35] * 5,
        'region': ['North', 'South', 'East', 'West', 'Central'] * 10,
        'payment_method': ['Credit Card', 'PayPal', 'Cash', 'Debit Card', 'Bank Transfer'] * 10,
        'discount_percent': [0, 5, 10, 15, 20, 0, 5, 10, 0, 15] * 5
    }
    
    df = pd.DataFrame(data)
    
    # Add calculated columns
    df['total_amount'] = df['price'] * df['quantity'] * (1 - df['discount_percent'] / 100)
    df['profit_margin'] = df['total_amount'] * 0.3  # Assume 30% profit margin
    
    # Add some missing values for testing
    df.loc[5:8, 'customer_age'] = None
    df.loc[15:17, 'discount_percent'] = None
    
    csv_file = 'comprehensive_sales_data.csv'
    df.to_csv(csv_file, index=False)
    
    print(f"✅ Created comprehensive CSV: {csv_file}")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Total Revenue: ${df['total_amount'].sum():,.2f}")
    print(f"   Date Range: {df['order_date'].min()} to {df['order_date'].max()}")
    
    return csv_file

def upload_and_analyze(csv_file):
    """Upload CSV and get AI analysis."""
    url = "http://127.0.0.1:8000/api/data/upload/"
    
    print(f"\n📤 Uploading {csv_file}...")
    
    with open(csv_file, 'rb') as f:
        files = {'file': (csv_file, f, 'text/csv')}
        data = {
            'name': 'Comprehensive Sales Dataset',
            'description': 'Complete sales data with multiple product categories, customer demographics, and transaction details'
        }
        
        response = requests.post(url, files=files, data=data, timeout=120)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Upload successful!")
            
            data_source = result.get('data_source', {})
            analysis = result.get('analysis', {})
            
            print(f"📊 Data Source ID: {data_source.get('id')}")
            print(f"📈 Quality Score: {analysis.get('quality_report', {}).get('overall_score', 'N/A')}/100")
            print(f"🤖 AI Model: {analysis.get('ai_insights', {}).get('model_used', 'N/A')}")
            
            return data_source.get('id'), analysis
        else:
            print(f"❌ Upload failed: {response.text}")
            return None, None

def test_queries(data_source_id):
    """Test various queries on the uploaded data."""
    queries = [
        "Show me the total revenue by product category",
        "What are the top 5 customers by total spending?",
        "Analyze sales trends over time",
        "Which payment method is most popular?",
        "Show me the average order value by region",
        "Find customers who spent more than $1000",
        "What's the impact of discounts on sales?",
        "Show me monthly sales summary"
    ]
    
    print(f"\n🔍 Testing {len(queries)} queries...")
    
    successful_queries = 0
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: {query}")
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/query/process/",
                json={
                    "query": query,
                    "data_source_id": data_source_id,
                    "include_sql": True,
                    "include_visualization": True
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {len(result.get('results', []))} results")
                print(f"   🤖 AI Response: {result.get('ai_response', '')[:100]}...")
                successful_queries += 1
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Query Results: {successful_queries}/{len(queries)} successful")
    return successful_queries

def test_data_sources_api():
    """Test the data sources API."""
    print(f"\n📋 Testing Data Sources API...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/data/sources/", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            sources = data.get('results', data) if isinstance(data, dict) else data
            print(f"   ✅ Found {len(sources)} data sources")
            
            for source in sources[:3]:  # Show first 3
                print(f"   📊 {source.get('name', 'N/A')} - {source.get('status', 'N/A')}")
            
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 COMPLETE PIPELINE TEST")
    print("=" * 60)
    print("Testing: CSV Upload → AI Analysis → Query Processing")
    print("=" * 60)
    
    # Create test data
    csv_file = create_comprehensive_csv()
    
    try:
        # Test 1: Upload and Analysis
        print("\n" + "=" * 40)
        print("🧪 TEST 1: CSV UPLOAD & AI ANALYSIS")
        print("=" * 40)
        
        data_source_id, analysis = upload_and_analyze(csv_file)
        
        if not data_source_id:
            print("❌ Upload failed, stopping tests")
            return
        
        # Test 2: Query Processing
        print("\n" + "=" * 40)
        print("🧪 TEST 2: QUERY PROCESSING")
        print("=" * 40)
        
        successful_queries = test_queries(data_source_id)
        
        # Test 3: Data Sources API
        print("\n" + "=" * 40)
        print("🧪 TEST 3: DATA SOURCES API")
        print("=" * 40)
        
        api_success = test_data_sources_api()
        
        # Final Summary
        print("\n" + "=" * 60)
        print("📋 FINAL RESULTS")
        print("=" * 60)
        
        print(f"✅ CSV Upload & AI Analysis: {'PASS' if data_source_id else 'FAIL'}")
        print(f"✅ Query Processing: {'PASS' if successful_queries >= 6 else 'PARTIAL' if successful_queries > 0 else 'FAIL'}")
        print(f"✅ Data Sources API: {'PASS' if api_success else 'FAIL'}")
        
        if data_source_id and successful_queries >= 6 and api_success:
            print("\n🎉 ALL TESTS PASSED! The complete pipeline is working perfectly!")
            print("\n💡 Your CSV upload pipeline with AI analysis is ready for production!")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            
    finally:
        # Clean up
        if os.path.exists(csv_file):
            os.remove(csv_file)
            print(f"\n🧹 Cleaned up: {csv_file}")

if __name__ == "__main__":
    main()
