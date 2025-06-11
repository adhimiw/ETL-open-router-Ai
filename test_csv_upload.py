#!/usr/bin/env python3
"""
Test script for CSV upload pipeline with AI analysis.
"""

import requests
import pandas as pd
import json
import os

def create_sample_csv():
    """Create a sample CSV file for testing."""
    # Create sample sales data
    data = {
        'date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'product': ['Product A', 'Product B', 'Product C'] * 33 + ['Product A'],
        'sales_amount': [100, 150, 200, 120, 180, 90, 250, 300, 80, 160] * 10,
        'quantity': [1, 2, 3, 1, 2, 1, 3, 4, 1, 2] * 10,
        'customer_id': range(1, 101),
        'region': ['North', 'South', 'East', 'West'] * 25,
        'discount': [0.0, 0.1, 0.05, 0.15, 0.0] * 20
    }
    
    df = pd.DataFrame(data)
    
    # Add some missing values for testing
    df.loc[5:10, 'discount'] = None
    df.loc[15:18, 'sales_amount'] = None
    
    # Save to CSV
    csv_file = 'sample_sales_data.csv'
    df.to_csv(csv_file, index=False)
    print(f"Created sample CSV file: {csv_file}")
    return csv_file

def test_csv_upload(csv_file):
    """Test the CSV upload endpoint."""
    url = "http://127.0.0.1:8000/api/data/upload/"
    
    try:
        # Prepare the file upload
        with open(csv_file, 'rb') as f:
            files = {
                'file': (csv_file, f, 'text/csv')
            }
            data = {
                'name': 'Sample Sales Data',
                'description': 'Test dataset with sales information for AI analysis'
            }
            
            print("Uploading CSV file...")
            print(f"File: {csv_file}")
            print(f"URL: {url}")
            print("-" * 60)
            
            response = requests.post(url, files=files, data=data, timeout=120)
            
            if response.status_code == 201:
                result = response.json()
                print("✅ CSV Upload Successful!")
                print("-" * 60)
                
                # Display basic info
                data_source = result.get('data_source', {})
                print(f"Data Source ID: {data_source.get('id')}")
                print(f"Name: {data_source.get('name')}")
                print(f"Status: {data_source.get('status')}")
                print(f"Rows: {data_source.get('rows_count', 'N/A')}")
                print(f"Columns: {data_source.get('columns_count', 'N/A')}")
                print(f"File Size: {data_source.get('file_size_mb', 'N/A')} MB")
                
                # Display analysis results
                analysis = result.get('analysis', {})
                if analysis:
                    print("\n" + "=" * 60)
                    print("📊 DATA ANALYSIS RESULTS")
                    print("=" * 60)
                    
                    # Data Summary
                    summary = analysis.get('data_summary', {})
                    if summary:
                        print(f"\n📋 Data Summary:")
                        print(f"   Total Rows: {summary.get('total_rows', 'N/A'):,}")
                        print(f"   Total Columns: {summary.get('total_columns', 'N/A')}")
                        print(f"   Memory Usage: {summary.get('memory_usage_mb', 'N/A')} MB")
                        print(f"   Columns: {', '.join(summary.get('column_names', []))}")
                    
                    # Sample Data
                    sample_data = analysis.get('sample_data', [])
                    if sample_data:
                        print(f"\n📄 Sample Data (first 3 rows):")
                        for i, row in enumerate(sample_data[:3]):
                            print(f"   Row {i+1}: {row}")
                    
                    # AI Insights
                    ai_insights = analysis.get('ai_insights', {})
                    if ai_insights:
                        print(f"\n🤖 AI Analysis:")
                        print(f"   Model: {ai_insights.get('model_used', 'N/A')}")
                        print(f"   Tokens Used: {ai_insights.get('tokens_used', 'N/A')}")
                        insights = ai_insights.get('insights', '')
                        if insights:
                            print(f"\n   Insights:")
                            # Print first 500 characters of insights
                            print(f"   {insights[:500]}...")
                    
                    # Quality Report
                    quality = analysis.get('quality_report', {})
                    if quality:
                        print(f"\n📈 Data Quality:")
                        print(f"   Overall Score: {quality.get('overall_score', 'N/A')}/100")
                        print(f"   Completeness: {quality.get('completeness_score', 'N/A'):.1f}%")
                        print(f"   Total Issues: {quality.get('total_issues', 'N/A')}")
                    
                    # Visualization Suggestions
                    viz_suggestions = analysis.get('visualization_suggestions', [])
                    if viz_suggestions:
                        print(f"\n📊 Visualization Suggestions:")
                        for i, viz in enumerate(viz_suggestions[:3]):
                            print(f"   {i+1}. {viz.get('title', 'N/A')} ({viz.get('chart_type', 'N/A')})")
                    
                    # Data Issues
                    issues = analysis.get('data_issues', [])
                    if issues:
                        print(f"\n⚠️  Data Issues Found:")
                        for issue in issues[:5]:  # Show first 5 issues
                            print(f"   - {issue.get('description', 'N/A')} ({issue.get('severity', 'N/A')})")
                    
                    # Recommendations
                    recommendations = analysis.get('recommendations', [])
                    if recommendations:
                        print(f"\n💡 Recommendations:")
                        for i, rec in enumerate(recommendations[:5]):
                            print(f"   {i+1}. {rec}")
                
                print("\n" + "=" * 60)
                print("🎉 CSV Upload and Analysis Complete!")
                
                return True
                
            else:
                print(f"❌ Upload failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing CSV Upload Pipeline with AI Analysis")
    print("=" * 60)
    
    # Create sample CSV
    csv_file = create_sample_csv()
    
    try:
        # Test upload
        success = test_csv_upload(csv_file)
        
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Tests failed!")
            
    finally:
        # Clean up
        if os.path.exists(csv_file):
            os.remove(csv_file)
            print(f"\nCleaned up: {csv_file}")

if __name__ == "__main__":
    main()
