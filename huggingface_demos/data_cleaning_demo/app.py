"""
EETL AI Platform - Data Cleaning Demo
Hugging Face Spaces Demo for AI-powered data cleaning and quality assessment
"""

import gradio as gr
import pandas as pd
import numpy as np
import openai
import json
import io
from typing import Dict, Any, Tuple, Optional

# Configure OpenRouter API
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = "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"

def analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze data quality and generate statistics."""
    
    analysis = {
        "basic_stats": {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "duplicate_rows": df.duplicated().sum()
        },
        "column_analysis": {},
        "data_types": df.dtypes.to_dict(),
        "missing_data": df.isnull().sum().to_dict(),
        "summary_stats": {}
    }
    
    # Analyze each column
    for col in df.columns:
        col_analysis = {
            "data_type": str(df[col].dtype),
            "null_count": df[col].isnull().sum(),
            "null_percentage": (df[col].isnull().sum() / len(df)) * 100,
            "unique_count": df[col].nunique(),
            "unique_percentage": (df[col].nunique() / len(df)) * 100
        }
        
        # Add type-specific analysis
        if df[col].dtype in ['int64', 'float64']:
            col_analysis.update({
                "min_value": df[col].min(),
                "max_value": df[col].max(),
                "mean_value": df[col].mean(),
                "std_deviation": df[col].std(),
                "outliers_count": len(df[col][(np.abs(df[col] - df[col].mean()) > 2 * df[col].std())])
            })
        elif df[col].dtype == 'object':
            col_analysis.update({
                "avg_length": df[col].astype(str).str.len().mean(),
                "max_length": df[col].astype(str).str.len().max(),
                "min_length": df[col].astype(str).str.len().min()
            })
        
        analysis["column_analysis"][col] = col_analysis
    
    # Generate summary statistics for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        analysis["summary_stats"] = df[numeric_cols].describe().to_dict()
    
    return analysis

def get_ai_recommendations(analysis: Dict[str, Any], sample_data: str) -> str:
    """Get AI-powered data cleaning recommendations."""
    
    prompt = f"""
    You are an expert data scientist. Analyze the following data quality report and provide specific, actionable recommendations for data cleaning and improvement.

    Data Quality Analysis:
    {json.dumps(analysis, indent=2, default=str)}

    Sample Data (first 5 rows):
    {sample_data}

    Please provide:
    1. Overall data quality assessment (score out of 100)
    2. Top 5 critical issues that need immediate attention
    3. Specific cleaning recommendations with Python code examples
    4. Data validation rules to implement
    5. Suggestions for data enrichment or transformation

    Format your response in clear sections with actionable steps.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert data quality analyst and data scientist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error getting AI recommendations: {str(e)}"

def generate_cleaning_code(analysis: Dict[str, Any], recommendations: str) -> str:
    """Generate Python code for data cleaning based on analysis and recommendations."""
    
    prompt = f"""
    Based on the data analysis and recommendations below, generate comprehensive Python code using pandas for data cleaning.

    Data Analysis:
    {json.dumps(analysis, indent=2, default=str)}

    Recommendations:
    {recommendations}

    Generate Python code that includes:
    1. Missing value handling
    2. Outlier detection and treatment
    3. Data type conversions
    4. Duplicate removal
    5. Data validation
    6. Column standardization

    Provide clean, well-commented code that can be executed directly.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert Python developer specializing in data cleaning with pandas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating cleaning code: {str(e)}"

def process_uploaded_file(file) -> Tuple[pd.DataFrame, str, str, str]:
    """Process uploaded file and return analysis results."""
    
    if file is None:
        return None, "Please upload a file first.", "", ""
    
    try:
        # Read the file based on extension
        if file.name.endswith('.csv'):
            df = pd.read_csv(file.name)
        elif file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file.name)
        elif file.name.endswith('.json'):
            df = pd.read_json(file.name)
        else:
            return None, "Unsupported file format. Please upload CSV, Excel, or JSON files.", "", ""
        
        # Limit size for demo
        if len(df) > 10000:
            df = df.head(10000)
            size_warning = f"\n⚠️ File truncated to 10,000 rows for demo purposes."
        else:
            size_warning = ""
        
        # Generate analysis
        analysis = analyze_data_quality(df)
        
        # Get sample data for AI
        sample_data = df.head().to_string()
        
        # Get AI recommendations
        recommendations = get_ai_recommendations(analysis, sample_data)
        
        # Generate cleaning code
        cleaning_code = generate_cleaning_code(analysis, recommendations)
        
        # Format analysis results
        analysis_text = f"""
## 📊 Data Quality Analysis Results{size_warning}

### Basic Statistics
- **Total Rows:** {analysis['basic_stats']['total_rows']:,}
- **Total Columns:** {analysis['basic_stats']['total_columns']}
- **Memory Usage:** {analysis['basic_stats']['memory_usage'] / 1024:.2f} KB
- **Duplicate Rows:** {analysis['basic_stats']['duplicate_rows']}

### Column Analysis
"""
        
        for col, col_analysis in analysis['column_analysis'].items():
            analysis_text += f"""
**{col}** ({col_analysis['data_type']})
- Null Values: {col_analysis['null_count']} ({col_analysis['null_percentage']:.1f}%)
- Unique Values: {col_analysis['unique_count']} ({col_analysis['unique_percentage']:.1f}%)
"""
            
            if 'outliers_count' in col_analysis:
                analysis_text += f"- Outliers: {col_analysis['outliers_count']}\n"
        
        return df, analysis_text, recommendations, cleaning_code
        
    except Exception as e:
        return None, f"Error processing file: {str(e)}", "", ""

def create_demo_interface():
    """Create the Gradio interface for the data cleaning demo."""
    
    with gr.Blocks(
        title="EETL AI Platform - Data Cleaning Demo",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .tab-nav {
            background: linear-gradient(90deg, #3b82f6, #1d4ed8);
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🤖 EETL AI Platform - Data Cleaning Demo
        
        **Transform your data quality with AI-powered analysis and recommendations**
        
        Upload your dataset and get instant AI-powered insights, quality assessment, and automated cleaning recommendations.
        
        ✨ **Features:**
        - Comprehensive data quality analysis
        - AI-powered cleaning recommendations
        - Automated Python code generation
        - Support for CSV, Excel, and JSON files
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="📁 Upload Your Dataset",
                    file_types=[".csv", ".xlsx", ".xls", ".json"],
                    type="file"
                )
                
                analyze_btn = gr.Button(
                    "🔍 Analyze Data Quality",
                    variant="primary",
                    size="lg"
                )
                
                gr.Markdown("""
                ### 📋 Supported Formats
                - **CSV** (.csv)
                - **Excel** (.xlsx, .xls)
                - **JSON** (.json)
                
                ### 🚀 What You'll Get
                1. **Data Quality Score** - Overall assessment
                2. **Issue Detection** - Missing values, outliers, duplicates
                3. **AI Recommendations** - Expert cleaning advice
                4. **Python Code** - Ready-to-use cleaning scripts
                """)
            
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.Tab("📊 Quality Analysis"):
                        analysis_output = gr.Markdown(
                            value="Upload a file and click 'Analyze Data Quality' to see detailed analysis results.",
                            label="Analysis Results"
                        )
                    
                    with gr.Tab("🎯 AI Recommendations"):
                        recommendations_output = gr.Markdown(
                            value="AI-powered recommendations will appear here after analysis.",
                            label="Cleaning Recommendations"
                        )
                    
                    with gr.Tab("💻 Python Code"):
                        code_output = gr.Code(
                            value="# Generated Python cleaning code will appear here",
                            language="python",
                            label="Data Cleaning Code"
                        )
                    
                    with gr.Tab("🔍 Data Preview"):
                        data_preview = gr.Dataframe(
                            label="Data Preview (First 100 rows)",
                            max_rows=100
                        )
        
        # Event handlers
        analyze_btn.click(
            fn=process_uploaded_file,
            inputs=[file_input],
            outputs=[data_preview, analysis_output, recommendations_output, code_output]
        )
        
        gr.Markdown("""
        ---
        
        ### 🌟 About EETL AI Platform
        
        This demo showcases the data cleaning capabilities of our comprehensive ETL platform. 
        The full platform includes:
        
        - **Natural Language Querying** - Ask questions about your data in plain English
        - **Automated Data Pipeline** - End-to-end ETL with AI assistance
        - **Interactive Visualizations** - Dynamic charts and reports
        - **Multi-source Integration** - Connect to databases, APIs, and files
        - **Collaborative Analytics** - Share insights with your team
        
        **🔗 Links:**
        - [GitHub Repository](https://github.com/adimiw/eetl-ai-platform)
        - [Full Platform Demo](https://eetl-ai-platform.com)
        - [Documentation](https://docs.eetl-ai-platform.com)
        
        **Built with ❤️ by [adimiw](https://github.com/adimiw)**
        """)
    
    return demo

if __name__ == "__main__":
    demo = create_demo_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )
