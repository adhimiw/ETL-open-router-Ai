#!/usr/bin/env python3
"""
Debug script to test CSV upload pipeline and identify issues.
"""

import requests
import pandas as pd
import json
import os
import time

def create_test_csv():
    """Create a test CSV with real data for debugging."""
    data = {
        'customer_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'customer_name': ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Brown', 
                         'Frank Miller', 'Grace Lee', 'Henry Taylor', 'Ivy Chen', 'Jack Anderson'],
        'product': ['Laptop', 'Phone', 'Tablet', 'Laptop', 'Phone', 'Headphones', 'Laptop', 'Tablet', 'Phone', 'Headphones'],
        'sales_amount': [1200.50, 899.99, 599.99, 1199.00, 799.99, 199.99, 1299.99, 649.99, 899.99, 149.99],
        'quantity': [1, 1, 2, 1, 1, 3, 1, 1, 2, 2],
        'order_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19',
                      '2024-01-20', '2024-01-21', '2024-01-22', '2024-01-23', '2024-01-24'],
        'region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West', 'North', 'South']
    }
    
    df = pd.DataFrame(data)
    csv_file = 'debug_sales_data.csv'
    df.to_csv(csv_file, index=False)
    print(f"✅ Created test CSV: {csv_file}")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Sample data:")
    print(df.head(3).to_string())
    return csv_file

def test_health_endpoint():
    """Test if the backend is responding."""
    try:
        response = requests.get("http://127.0.0.1:8000/api/health/", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False

def test_upload_endpoint(csv_file):
    """Test the upload endpoint with detailed debugging."""
    url = "http://127.0.0.1:8000/api/data/upload/"
    
    print(f"\n🔍 Testing upload endpoint: {url}")
    print(f"📁 File: {csv_file}")
    print(f"📊 File size: {os.path.getsize(csv_file)} bytes")
    
    try:
        with open(csv_file, 'rb') as f:
            files = {
                'file': (csv_file, f, 'text/csv')
            }
            data = {
                'name': 'Debug Sales Data',
                'description': 'Test CSV for debugging upload pipeline'
            }
            
            print("📤 Uploading file...")
            start_time = time.time()
            
            response = requests.post(url, files=files, data=data, timeout=120)
            
            upload_time = time.time() - start_time
            print(f"⏱️  Upload completed in {upload_time:.2f} seconds")
            print(f"📋 Response status: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print("✅ Upload successful!")
                
                # Check data source info
                data_source = result.get('data_source', {})
                print(f"\n📊 Data Source Info:")
                print(f"   ID: {data_source.get('id')}")
                print(f"   Name: {data_source.get('name')}")
                print(f"   Status: {data_source.get('status')}")
                print(f"   Rows: {data_source.get('rows_count')}")
                print(f"   Columns: {data_source.get('columns_count')}")
                
                # Check analysis results
                analysis = result.get('analysis', {})
                if analysis:
                    print(f"\n🤖 AI Analysis Results:")
                    
                    # Data summary
                    summary = analysis.get('data_summary', {})
                    if summary:
                        print(f"   Total Rows: {summary.get('total_rows')}")
                        print(f"   Total Columns: {summary.get('total_columns')}")
                        print(f"   Column Names: {summary.get('column_names')}")
                    
                    # AI insights
                    ai_insights = analysis.get('ai_insights', {})
                    if ai_insights:
                        print(f"   AI Model: {ai_insights.get('model_used')}")
                        print(f"   Tokens Used: {ai_insights.get('tokens_used')}")
                        insights = ai_insights.get('insights', '')
                        if insights:
                            print(f"   AI Insights (first 200 chars): {insights[:200]}...")
                    
                    # Sample data
                    sample_data = analysis.get('sample_data', [])
                    if sample_data:
                        print(f"   Sample Data (first row): {sample_data[0] if sample_data else 'None'}")
                    
                    # Quality report
                    quality = analysis.get('quality_report', {})
                    if quality:
                        print(f"   Quality Score: {quality.get('overall_score', 'N/A')}")
                    
                    # Issues
                    issues = analysis.get('data_issues', [])
                    print(f"   Data Issues Found: {len(issues)}")
                    
                    # Recommendations
                    recommendations = analysis.get('recommendations', [])
                    print(f"   Recommendations: {len(recommendations)}")
                
                return True
                
            else:
                print(f"❌ Upload failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_query_endpoint():
    """Test the query processing endpoint."""
    url = "http://127.0.0.1:8000/api/query/process/"
    
    print(f"\n🔍 Testing query endpoint: {url}")
    
    try:
        payload = {
            "query": "Show me a summary of the sales data including total revenue and top products",
            "include_sql": True,
            "include_visualization": True
        }
        
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"📋 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query processing successful!")
            print(f"   Query: {result.get('query')}")
            print(f"   AI Response: {result.get('ai_response', '')[:200]}...")
            print(f"   Results: {len(result.get('results', []))} rows")
            print(f"   Model: {result.get('model')}")
            return True
        else:
            print(f"❌ Query failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query error: {e}")
        return False

def main():
    """Main debugging function."""
    print("🐛 CSV Upload Pipeline Debug Tool")
    print("=" * 60)
    
    # Test backend connection
    if not test_health_endpoint():
        print("❌ Backend is not responding. Please start the Django server.")
        return
    
    # Create test CSV
    csv_file = create_test_csv()
    
    try:
        # Test upload
        print("\n" + "=" * 60)
        print("🧪 TESTING CSV UPLOAD")
        print("=" * 60)
        
        upload_success = test_upload_endpoint(csv_file)
        
        # Test query processing
        print("\n" + "=" * 60)
        print("🧪 TESTING QUERY PROCESSING")
        print("=" * 60)
        
        query_success = test_query_endpoint()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 DEBUG SUMMARY")
        print("=" * 60)
        print(f"✅ Backend Health: OK")
        print(f"{'✅' if upload_success else '❌'} CSV Upload: {'OK' if upload_success else 'FAILED'}")
        print(f"{'✅' if query_success else '❌'} Query Processing: {'OK' if query_success else 'FAILED'}")
        
        if upload_success and query_success:
            print("\n🎉 All tests passed! The pipeline is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            
    finally:
        # Clean up
        if os.path.exists(csv_file):
            os.remove(csv_file)
            print(f"\n🧹 Cleaned up: {csv_file}")

if __name__ == "__main__":
    main()
