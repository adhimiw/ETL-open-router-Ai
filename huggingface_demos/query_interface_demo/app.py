"""
EETL AI Platform - Natural Language Query Interface Demo
Hugging Face Spaces Demo for AI-powered data querying and analysis
"""

import gradio as gr
import pandas as pd
import numpy as np
import openai
import sqlite3
import json
import io
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Tuple, Optional, List

# Configure OpenRouter API
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = "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"

# Sample datasets for demo
SAMPLE_DATASETS = {
    "Sales Data": {
        "description": "E-commerce sales data with products, customers, and transactions",
        "data": pd.DataFrame({
            "order_id": range(1, 101),
            "customer_id": np.random.randint(1, 21, 100),
            "product_category": np.random.choice(["Electronics", "Clothing", "Books", "Home", "Sports"], 100),
            "product_name": [f"Product_{i}" for i in range(1, 101)],
            "quantity": np.random.randint(1, 6, 100),
            "unit_price": np.round(np.random.uniform(10, 500, 100), 2),
            "total_amount": None,  # Will be calculated
            "order_date": pd.date_range("2023-01-01", periods=100, freq="D")[:100],
            "customer_age": np.random.randint(18, 70, 100),
            "customer_city": np.random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"], 100)
        })
    },
    "Employee Data": {
        "description": "HR employee data with salaries, departments, and performance",
        "data": pd.DataFrame({
            "employee_id": range(1, 51),
            "name": [f"Employee_{i}" for i in range(1, 51)],
            "department": np.random.choice(["Engineering", "Sales", "Marketing", "HR", "Finance"], 50),
            "position": np.random.choice(["Junior", "Senior", "Manager", "Director"], 50),
            "salary": np.random.randint(40000, 150000, 50),
            "years_experience": np.random.randint(0, 20, 50),
            "performance_score": np.round(np.random.uniform(3.0, 5.0, 50), 1),
            "hire_date": pd.date_range("2015-01-01", "2023-01-01", periods=50),
            "age": np.random.randint(22, 65, 50),
            "education": np.random.choice(["Bachelor", "Master", "PhD"], 50)
        })
    },
    "Stock Prices": {
        "description": "Stock market data with prices and trading volumes",
        "data": pd.DataFrame({
            "date": pd.date_range("2023-01-01", periods=252, freq="D"),
            "symbol": np.random.choice(["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"], 252),
            "open_price": np.round(np.random.uniform(100, 300, 252), 2),
            "high_price": None,  # Will be calculated
            "low_price": None,   # Will be calculated
            "close_price": None, # Will be calculated
            "volume": np.random.randint(1000000, 10000000, 252),
            "market_cap": np.random.randint(1000000000, 3000000000, 252)
        })
    }
}

# Calculate derived fields
for dataset_name, dataset_info in SAMPLE_DATASETS.items():
    df = dataset_info["data"]
    
    if dataset_name == "Sales Data":
        df["total_amount"] = df["quantity"] * df["unit_price"]
    
    elif dataset_name == "Stock Prices":
        df["high_price"] = df["open_price"] * np.random.uniform(1.0, 1.1, len(df))
        df["low_price"] = df["open_price"] * np.random.uniform(0.9, 1.0, len(df))
        df["close_price"] = df["open_price"] * np.random.uniform(0.95, 1.05, len(df))

def create_database_from_dataframe(df: pd.DataFrame, table_name: str) -> sqlite3.Connection:
    """Create SQLite database from DataFrame."""
    conn = sqlite3.connect(":memory:")
    df.to_sql(table_name, conn, index=False, if_exists="replace")
    return conn

def get_table_schema(conn: sqlite3.Connection, table_name: str) -> str:
    """Get table schema information."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    schema = f"Table: {table_name}\nColumns:\n"
    for col in columns:
        schema += f"  - {col[1]} ({col[2]})\n"
    
    return schema

def generate_sql_query(natural_language_query: str, schema: str, sample_data: str) -> str:
    """Generate SQL query from natural language using AI."""
    
    prompt = f"""
    You are an expert SQL query generator. Convert the natural language query into a valid SQL query.

    Database Schema:
    {schema}

    Sample Data (first 3 rows):
    {sample_data}

    Natural Language Query: "{natural_language_query}"

    Rules:
    1. Generate only the SQL query, no explanations
    2. Use proper SQL syntax for SQLite
    3. Handle aggregations, filters, and joins appropriately
    4. Ensure the query is safe and doesn't modify data
    5. Use appropriate column names from the schema

    SQL Query:
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert SQL developer. Generate only valid SQL queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Clean up the response to extract just the SQL
        if "```sql" in sql_query:
            sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql_query:
            sql_query = sql_query.split("```")[1].strip()
        
        return sql_query
    
    except Exception as e:
        return f"-- Error generating SQL: {str(e)}"

def execute_sql_query(conn: sqlite3.Connection, sql_query: str) -> Tuple[pd.DataFrame, str]:
    """Execute SQL query and return results."""
    
    try:
        result_df = pd.read_sql_query(sql_query, conn)
        return result_df, "Query executed successfully!"
    
    except Exception as e:
        return pd.DataFrame(), f"Error executing query: {str(e)}"

def generate_insights(query: str, results: pd.DataFrame) -> str:
    """Generate AI-powered insights from query results."""
    
    if results.empty:
        return "No data to analyze."
    
    # Prepare data summary for AI
    data_summary = {
        "query": query,
        "row_count": len(results),
        "columns": list(results.columns),
        "sample_data": results.head(3).to_dict('records') if len(results) > 0 else [],
        "data_types": results.dtypes.to_dict()
    }
    
    # Add statistical summary for numeric columns
    numeric_cols = results.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        data_summary["statistics"] = results[numeric_cols].describe().to_dict()
    
    prompt = f"""
    Analyze the following query results and provide meaningful business insights.

    Query: "{query}"
    
    Data Summary:
    {json.dumps(data_summary, indent=2, default=str)}

    Provide:
    1. Key findings and patterns
    2. Business insights and implications
    3. Recommendations for further analysis
    4. Notable trends or anomalies

    Keep the analysis concise but insightful.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert data analyst providing business insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating insights: {str(e)}"

def create_visualization(results: pd.DataFrame, query: str) -> Optional[go.Figure]:
    """Create appropriate visualization based on query results."""
    
    if results.empty or len(results) == 0:
        return None
    
    try:
        # Determine best visualization type
        numeric_cols = results.select_dtypes(include=[np.number]).columns
        categorical_cols = results.select_dtypes(include=['object']).columns
        
        if len(results) == 1:
            # Single row - show as metrics
            fig = go.Figure()
            for i, col in enumerate(results.columns):
                fig.add_trace(go.Indicator(
                    mode="number",
                    value=results[col].iloc[0],
                    title={"text": col},
                    domain={'row': 0, 'column': i}
                ))
            fig.update_layout(
                grid={'rows': 1, 'columns': len(results.columns)},
                title="Query Results"
            )
            
        elif len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            # Bar chart for categorical vs numeric
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            if len(results) <= 20:  # Avoid overcrowded charts
                fig = px.bar(
                    results, 
                    x=cat_col, 
                    y=num_col,
                    title=f"{num_col} by {cat_col}"
                )
            else:
                # Use aggregation for large datasets
                agg_data = results.groupby(cat_col)[num_col].sum().reset_index()
                fig = px.bar(
                    agg_data,
                    x=cat_col,
                    y=num_col,
                    title=f"Total {num_col} by {cat_col}"
                )
                
        elif len(numeric_cols) >= 2:
            # Scatter plot for two numeric columns
            fig = px.scatter(
                results,
                x=numeric_cols[0],
                y=numeric_cols[1],
                title=f"{numeric_cols[1]} vs {numeric_cols[0]}"
            )
            
        elif len(numeric_cols) == 1:
            # Histogram for single numeric column
            fig = px.histogram(
                results,
                x=numeric_cols[0],
                title=f"Distribution of {numeric_cols[0]}"
            )
            
        else:
            # Default to showing data counts
            if len(categorical_cols) > 0:
                value_counts = results[categorical_cols[0]].value_counts()
                fig = px.pie(
                    values=value_counts.values,
                    names=value_counts.index,
                    title=f"Distribution of {categorical_cols[0]}"
                )
            else:
                return None
        
        fig.update_layout(
            height=400,
            showlegend=True,
            template="plotly_white"
        )
        
        return fig
        
    except Exception as e:
        print(f"Visualization error: {str(e)}")
        return None

def process_natural_language_query(dataset_name: str, query: str) -> Tuple[str, pd.DataFrame, str, str, Optional[go.Figure]]:
    """Process natural language query and return results."""
    
    if not dataset_name or not query:
        return "", pd.DataFrame(), "Please select a dataset and enter a query.", "", None
    
    try:
        # Get dataset
        dataset_info = SAMPLE_DATASETS[dataset_name]
        df = dataset_info["data"].copy()
        
        # Create database
        table_name = "data_table"
        conn = create_database_from_dataframe(df, table_name)
        
        # Get schema
        schema = get_table_schema(conn, table_name)
        sample_data = df.head(3).to_string()
        
        # Generate SQL query
        sql_query = generate_sql_query(query, schema, sample_data)
        
        # Execute query
        results, execution_status = execute_sql_query(conn, sql_query)
        
        # Generate insights
        insights = generate_insights(query, results)
        
        # Create visualization
        visualization = create_visualization(results, query)
        
        conn.close()
        
        return sql_query, results, execution_status, insights, visualization
        
    except Exception as e:
        return "", pd.DataFrame(), f"Error processing query: {str(e)}", "", None

def create_demo_interface():
    """Create the Gradio interface for the query demo."""
    
    with gr.Blocks(
        title="EETL AI Platform - Natural Language Query Demo",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1400px !important;
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🤖 EETL AI Platform - Natural Language Query Interface
        
        **Ask questions about your data in plain English and get instant SQL queries, results, and insights!**
        
        This demo showcases how you can interact with data using natural language. Simply select a dataset, 
        ask a question in plain English, and watch as AI converts it to SQL, executes the query, and provides insights.
        
        ✨ **Features:**
        - Natural language to SQL conversion
        - Instant query execution
        - AI-powered insights generation
        - Automatic data visualization
        - Multiple sample datasets
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                dataset_dropdown = gr.Dropdown(
                    choices=list(SAMPLE_DATASETS.keys()),
                    label="📊 Select Dataset",
                    value="Sales Data",
                    info="Choose a sample dataset to query"
                )
                
                dataset_info = gr.Markdown(
                    value=SAMPLE_DATASETS["Sales Data"]["description"],
                    label="Dataset Description"
                )
                
                query_input = gr.Textbox(
                    label="💬 Ask a Question",
                    placeholder="e.g., 'Show me total sales by product category' or 'What are the top 5 customers by revenue?'",
                    lines=3
                )
                
                query_btn = gr.Button(
                    "🔍 Query Data",
                    variant="primary",
                    size="lg"
                )
                
                gr.Markdown("""
                ### 💡 Example Questions
                
                **Sales Data:**
                - "What are the total sales by category?"
                - "Show me the top 10 customers by revenue"
                - "What's the average order value by city?"
                
                **Employee Data:**
                - "What's the average salary by department?"
                - "Show me employees with performance score > 4.5"
                - "How many employees were hired each year?"
                
                **Stock Prices:**
                - "What's the average closing price by symbol?"
                - "Show me the highest volume trading days"
                - "Which stock had the biggest price change?"
                """)
            
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.Tab("📋 Query Results"):
                        with gr.Row():
                            with gr.Column():
                                sql_output = gr.Code(
                                    label="Generated SQL Query",
                                    language="sql",
                                    value="-- Your generated SQL query will appear here"
                                )
                                
                                execution_status = gr.Textbox(
                                    label="Execution Status",
                                    value="Ready to execute query..."
                                )
                        
                        results_table = gr.Dataframe(
                            label="Query Results",
                            max_rows=50
                        )
                    
                    with gr.Tab("🎯 AI Insights"):
                        insights_output = gr.Markdown(
                            value="AI-generated insights will appear here after running a query.",
                            label="Business Insights"
                        )
                    
                    with gr.Tab("📈 Visualization"):
                        chart_output = gr.Plot(
                            label="Data Visualization"
                        )
                    
                    with gr.Tab("🔍 Data Preview"):
                        data_preview = gr.Dataframe(
                            label="Dataset Preview (First 100 rows)",
                            value=SAMPLE_DATASETS["Sales Data"]["data"].head(100),
                            max_rows=100
                        )
        
        # Event handlers
        def update_dataset_info(dataset_name):
            if dataset_name in SAMPLE_DATASETS:
                info = SAMPLE_DATASETS[dataset_name]["description"]
                preview = SAMPLE_DATASETS[dataset_name]["data"].head(100)
                return info, preview
            return "", pd.DataFrame()
        
        dataset_dropdown.change(
            fn=update_dataset_info,
            inputs=[dataset_dropdown],
            outputs=[dataset_info, data_preview]
        )
        
        query_btn.click(
            fn=process_natural_language_query,
            inputs=[dataset_dropdown, query_input],
            outputs=[sql_output, results_table, execution_status, insights_output, chart_output]
        )
        
        gr.Markdown("""
        ---
        
        ### 🌟 About EETL AI Platform
        
        This demo showcases the natural language querying capabilities of our comprehensive ETL platform. 
        The full platform includes:
        
        - **AI-Powered Data Cleaning** - Automated quality assessment and cleaning
        - **Multi-Source Integration** - Connect to databases, APIs, files, and more
        - **Interactive Dashboards** - Build and share dynamic visualizations
        - **Automated ETL Pipelines** - Schedule and monitor data workflows
        - **Collaborative Analytics** - Team-based data exploration and sharing
        
        **🔗 Links:**
        - [GitHub Repository](https://github.com/adimiw/eetl-ai-platform)
        - [Data Cleaning Demo](https://huggingface.co/spaces/adimiw/eetl-data-cleaning-demo)
        - [Full Platform](https://eetl-ai-platform.com)
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
