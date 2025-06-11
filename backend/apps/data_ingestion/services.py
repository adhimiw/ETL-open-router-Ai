"""
Services for data ingestion and processing.
"""

import pandas as pd
import numpy as np
import json
import logging
import time
from typing import Dict, Any, List, Optional
from django.conf import settings
from celery import shared_task
import sqlalchemy
import requests
from io import StringIO

from .models import DataSource, DataColumn, DataQualityReport, DataTransformation
from apps.ai_engine.services import OpenRouterService

logger = logging.getLogger(__name__)


class DataIngestionService:
    """
    Service for data ingestion operations.
    """
    
    def __init__(self):
        self.supported_file_types = ['csv', 'xlsx', 'xls', 'json', 'parquet']
        self.supported_db_types = ['postgresql', 'mysql', 'sqlite', 'oracle', 'mssql']
    
    def read_file_data(self, file_path: str, file_type: str) -> pd.DataFrame:
        """
        Read data from uploaded file.
        """
        try:
            # Normalize file type - handle both MIME types and extensions
            if file_type in ['text/csv', 'csv']:
                file_type = 'csv'
            elif file_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xlsx']:
                file_type = 'xlsx'
            elif file_type in ['application/vnd.ms-excel', 'xls']:
                file_type = 'xls'
            elif file_type in ['application/json', 'json']:
                file_type = 'json'
            elif file_type in ['application/parquet', 'parquet']:
                file_type = 'parquet'

            # If still not recognized, try to detect from file extension
            if file_type not in ['csv', 'xlsx', 'xls', 'json', 'parquet']:
                file_extension = file_path.split('.')[-1].lower()
                if file_extension in ['csv', 'xlsx', 'xls', 'json', 'parquet']:
                    file_type = file_extension

            if file_type == 'csv':
                # Try different encodings and separators
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not decode CSV file with any supported encoding")

            elif file_type in ['xlsx', 'xls']:
                df = pd.read_excel(file_path)

            elif file_type == 'json':
                df = pd.read_json(file_path)

            elif file_type == 'parquet':
                df = pd.read_parquet(file_path)

            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            return df

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise
    
    def read_database_data(self, connection_params: Dict[str, Any], query: str = None) -> pd.DataFrame:
        """
        Read data from database connection.
        """
        try:
            # Build connection string
            db_type = connection_params['db_type']
            
            if db_type == 'postgresql':
                connection_string = (
                    f"postgresql://{connection_params['db_username']}:"
                    f"{connection_params['db_password']}@"
                    f"{connection_params['db_host']}:"
                    f"{connection_params['db_port']}/"
                    f"{connection_params['db_name']}"
                )
            elif db_type == 'mysql':
                connection_string = (
                    f"mysql+pymysql://{connection_params['db_username']}:"
                    f"{connection_params['db_password']}@"
                    f"{connection_params['db_host']}:"
                    f"{connection_params['db_port']}/"
                    f"{connection_params['db_name']}"
                )
            elif db_type == 'sqlite':
                connection_string = f"sqlite:///{connection_params['db_name']}"
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Create engine and read data
            engine = sqlalchemy.create_engine(connection_string)
            
            if query:
                df = pd.read_sql_query(query, engine)
            else:
                table_name = connection_params.get('db_table')
                if not table_name:
                    raise ValueError("Either query or table name must be provided")
                df = pd.read_sql_table(table_name, engine)
            
            engine.dispose()
            return df
        
        except Exception as e:
            logger.error(f"Error reading database data: {str(e)}")
            raise
    
    def read_api_data(self, api_params: Dict[str, Any]) -> pd.DataFrame:
        """
        Read data from API endpoint.
        """
        try:
            # Prepare request
            url = api_params['api_url']
            method = api_params.get('api_method', 'GET')
            headers = api_params.get('api_headers', {})
            params = api_params.get('api_params', {})
            
            # Add authentication
            auth_type = api_params.get('api_auth_type', 'none')
            if auth_type == 'bearer':
                headers['Authorization'] = f"Bearer {api_params['api_auth_token']}"
            elif auth_type == 'api_key':
                headers['X-API-Key'] = api_params['api_auth_token']
            
            # Make request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse response
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                data = response.json()
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    # Try to find the data array in the response
                    for key in ['data', 'results', 'items', 'records']:
                        if key in data and isinstance(data[key], list):
                            df = pd.DataFrame(data[key])
                            break
                    else:
                        # If no array found, treat the dict as a single record
                        df = pd.DataFrame([data])
                else:
                    raise ValueError("Unsupported JSON structure")
            
            elif 'text/csv' in content_type:
                df = pd.read_csv(StringIO(response.text))
            
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            return df
        
        except Exception as e:
            logger.error(f"Error reading API data: {str(e)}")
            raise
    
    def test_database_connection(self, connection_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test database connection.
        """
        try:
            # Build connection string
            db_type = connection_params['db_type']
            
            if db_type == 'postgresql':
                connection_string = (
                    f"postgresql://{connection_params['db_username']}:"
                    f"{connection_params['db_password']}@"
                    f"{connection_params['db_host']}:"
                    f"{connection_params['db_port']}/"
                    f"{connection_params['db_name']}"
                )
            elif db_type == 'mysql':
                connection_string = (
                    f"mysql+pymysql://{connection_params['db_username']}:"
                    f"{connection_params['db_password']}@"
                    f"{connection_params['db_host']}:"
                    f"{connection_params['db_port']}/"
                    f"{connection_params['db_name']}"
                )
            elif db_type == 'sqlite':
                connection_string = f"sqlite:///{connection_params['db_name']}"
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Test connection
            engine = sqlalchemy.create_engine(connection_string)
            with engine.connect() as conn:
                # Get database info
                if db_type == 'postgresql':
                    result = conn.execute(sqlalchemy.text("SELECT version()"))
                    version = result.fetchone()[0]
                elif db_type == 'mysql':
                    result = conn.execute(sqlalchemy.text("SELECT VERSION()"))
                    version = result.fetchone()[0]
                else:
                    version = "Connected successfully"
                
                # Get table list
                inspector = sqlalchemy.inspect(engine)
                tables = inspector.get_table_names()
            
            engine.dispose()
            
            return {
                'version': version,
                'tables': tables[:20],  # Limit to first 20 tables
                'table_count': len(tables)
            }
        
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            raise
    
    def test_api_connection(self, api_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test API connection.
        """
        try:
            # Prepare request
            url = api_params['api_url']
            method = api_params.get('api_method', 'GET')
            headers = api_params.get('api_headers', {})
            params = api_params.get('api_params', {})
            
            # Add authentication
            auth_type = api_params.get('api_auth_type', 'none')
            if auth_type == 'bearer':
                headers['Authorization'] = f"Bearer {api_params['api_auth_token']}"
            elif auth_type == 'api_key':
                headers['X-API-Key'] = api_params['api_auth_token']
            
            # Make request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            return {
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'content_length': len(response.content),
                'response_time': response.elapsed.total_seconds()
            }
        
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}")
            raise
    
    def get_data_preview(self, data_source: DataSource, limit: int = 100, 
                        offset: int = 0, columns: List[str] = None, 
                        filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get preview of data source.
        """
        try:
            # Read data based on source type
            if data_source.source_type == 'file':
                df = self.read_file_data(
                    data_source.file.path,
                    data_source.file_type
                )
            elif data_source.source_type == 'database':
                connection_params = {
                    'db_type': data_source.db_type,
                    'db_host': data_source.db_host,
                    'db_port': data_source.db_port,
                    'db_name': data_source.db_name,
                    'db_username': data_source.db_username,
                    'db_password': data_source.db_password,
                    'db_table': data_source.db_table,
                }
                df = self.read_database_data(connection_params, data_source.db_query)
            elif data_source.source_type == 'api':
                api_params = {
                    'api_url': data_source.api_url,
                    'api_method': data_source.api_method,
                    'api_headers': data_source.api_headers,
                    'api_params': data_source.api_params,
                    'api_auth_type': data_source.api_auth_type,
                    'api_auth_token': data_source.api_auth_token,
                }
                df = self.read_api_data(api_params)
            else:
                raise ValueError(f"Unsupported source type: {data_source.source_type}")
            
            # Apply filters
            if filters:
                for column, value in filters.items():
                    if column in df.columns:
                        df = df[df[column] == value]
            
            # Select columns
            if columns:
                available_columns = [col for col in columns if col in df.columns]
                if available_columns:
                    df = df[available_columns]
            
            # Apply pagination
            total_rows = len(df)
            df_page = df.iloc[offset:offset + limit]
            
            # Convert to JSON-serializable format
            preview_data = df_page.fillna('').to_dict('records')
            
            return {
                'data': preview_data,
                'total_rows': total_rows,
                'columns': list(df.columns),
                'data_types': df.dtypes.astype(str).to_dict(),
                'offset': offset,
                'limit': limit
            }
        
        except Exception as e:
            logger.error(f"Error getting data preview: {str(e)}")
            raise
    
    @shared_task
    def process_file_upload(self, data_source_id: int):
        """
        Process uploaded file asynchronously.
        """
        try:
            data_source = DataSource.objects.get(id=data_source_id)
            data_source.status = 'processing'
            data_source.save()
            
            # Read and analyze file
            df = self.read_file_data(
                data_source.file.path,
                data_source.file_type
            )
            
            # Update data source with basic info
            data_source.rows_count = len(df)
            data_source.columns_count = len(df.columns)
            data_source.status = 'completed'
            data_source.save()
            
            # Create column records
            self._create_column_records(data_source, df)
            
            # Generate quality report
            analysis_service = DataAnalysisService()
            analysis_service.generate_quality_report(data_source, df)
            
            logger.info(f"Successfully processed data source {data_source_id}")

        except Exception as e:
            logger.error(f"Error processing data source {data_source_id}: {str(e)}")
            data_source = DataSource.objects.get(id=data_source_id)
            data_source.status = 'failed'
            data_source.error_message = str(e)
            data_source.save()

    def process_file_upload_with_ai(self, data_source_id: int) -> Dict[str, Any]:
        """
        Process uploaded file with AI-powered analysis and suggestions.
        """
        try:
            data_source = DataSource.objects.get(id=data_source_id)
            data_source.status = 'processing'
            data_source.save()

            # Read and analyze file
            file_extension = data_source.file.name.split('.')[-1].lower()
            df = self.read_file_data(data_source.file.path, file_extension)

            # Update data source with basic info
            data_source.rows_count = len(df)
            data_source.columns_count = len(df.columns)
            data_source.status = 'completed'
            data_source.save()

            # Create column records
            self._create_column_records(data_source, df)

            # Generate quality report
            analysis_service = DataAnalysisService()
            quality_report = analysis_service.generate_quality_report(data_source, df)

            # Generate AI-powered insights and suggestions
            ai_analysis = self._generate_ai_analysis(df, data_source)

            # Combine all analysis results
            complete_analysis = {
                'data_summary': {
                    'total_rows': len(df),
                    'total_columns': len(df.columns),
                    'file_size_mb': data_source.file_size_mb,
                    'column_names': list(df.columns),
                    'data_types': df.dtypes.astype(str).to_dict(),
                    'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
                },
                'sample_data': df.head(10).fillna('').to_dict('records'),
                'column_statistics': self._get_detailed_column_stats(df),
                'quality_report': quality_report,
                'ai_insights': ai_analysis,
                'visualization_suggestions': self._generate_visualization_suggestions(df),
                'data_issues': self._identify_data_issues(df),
                'recommendations': self._generate_data_recommendations(df, ai_analysis)
            }

            logger.info(f"Successfully processed data source {data_source_id} with AI analysis")
            return complete_analysis

        except Exception as e:
            logger.error(f"Error processing data source {data_source_id}: {str(e)}")
            data_source = DataSource.objects.get(id=data_source_id)
            data_source.status = 'failed'
            data_source.error_message = str(e)
            data_source.save()
            raise
    
    def _create_column_records(self, data_source: DataSource, df: pd.DataFrame):
        """
        Create column records for data source.
        """
        for column_name in df.columns:
            column_data = df[column_name]
            
            # Determine data type
            if pd.api.types.is_numeric_dtype(column_data):
                if pd.api.types.is_integer_dtype(column_data):
                    data_type = 'integer'
                else:
                    data_type = 'float'
            elif pd.api.types.is_datetime64_any_dtype(column_data):
                data_type = 'datetime'
            elif pd.api.types.is_bool_dtype(column_data):
                data_type = 'boolean'
            else:
                data_type = 'string'
            
            # Calculate statistics
            null_count = column_data.isnull().sum()
            unique_count = column_data.nunique()
            
            column_stats = {
                'null_count': int(null_count),
                'unique_count': int(unique_count),
            }
            
            # Add type-specific statistics
            if data_type in ['integer', 'float']:
                column_stats.update({
                    'min_value': str(column_data.min()),
                    'max_value': str(column_data.max()),
                    'mean_value': float(column_data.mean()),
                    'std_deviation': float(column_data.std()),
                })
                
                # Detect outliers
                q1 = column_data.quantile(0.25)
                q3 = column_data.quantile(0.75)
                iqr = q3 - q1
                outliers = column_data[
                    (column_data < q1 - 1.5 * iqr) | 
                    (column_data > q3 + 1.5 * iqr)
                ]
                column_stats.update({
                    'has_outliers': len(outliers) > 0,
                    'outlier_count': len(outliers),
                })
            
            # Sample values and value counts
            sample_values = column_data.dropna().head(10).tolist()
            value_counts = column_data.value_counts().head(10).to_dict()
            
            # Create column record
            DataColumn.objects.create(
                data_source=data_source,
                name=column_name,
                original_name=column_name,
                data_type=data_type,
                is_nullable=null_count > 0,
                sample_values=sample_values,
                value_counts=value_counts,
                **column_stats
            )

    def _generate_ai_analysis(self, df: pd.DataFrame, data_source: DataSource) -> Dict[str, Any]:
        """
        Generate AI-powered insights and analysis suggestions.
        """
        try:
            # Prepare data summary for AI
            data_summary = {
                'dataset_name': data_source.name,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': []
            }

            # Add column information
            for col in df.columns:
                col_info = {
                    'name': col,
                    'type': str(df[col].dtype),
                    'null_count': int(df[col].isnull().sum()),
                    'unique_count': int(df[col].nunique()),
                    'sample_values': df[col].dropna().head(5).tolist()
                }

                if pd.api.types.is_numeric_dtype(df[col]):
                    col_info.update({
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'mean': float(df[col].mean()),
                        'std': float(df[col].std())
                    })

                data_summary['columns'].append(col_info)

            # Create AI prompt
            prompt = f"""
            Analyze this dataset and provide insights and suggestions:

            Dataset: {data_summary['dataset_name']}
            Rows: {data_summary['total_rows']:,}
            Columns: {data_summary['total_columns']}

            Column Details:
            """

            for col in data_summary['columns'][:10]:  # Limit to first 10 columns
                prompt += f"\n- {col['name']} ({col['type']}): {col['unique_count']} unique values"
                if col['null_count'] > 0:
                    prompt += f", {col['null_count']} nulls"
                if 'mean' in col:
                    prompt += f", mean: {col['mean']:.2f}"

            prompt += """

            Please provide:
            1. Key insights about this dataset
            2. Potential data quality issues to watch for
            3. Suggested analysis approaches
            4. Business questions this data could answer
            5. Recommended data transformations

            Be specific and actionable in your recommendations.
            """

            # Get AI response
            openrouter_service = OpenRouterService()
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert data analyst. Provide detailed, actionable insights about datasets."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            ai_response = openrouter_service.chat_completion(messages)

            return {
                'insights': ai_response['content'],
                'model_used': ai_response['model'],
                'tokens_used': ai_response['tokens_used'],
                'analysis_timestamp': pd.Timestamp.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating AI analysis: {str(e)}")
            return {
                'insights': "AI analysis temporarily unavailable. Please try again later.",
                'error': str(e),
                'analysis_timestamp': pd.Timestamp.now().isoformat()
            }

    def _get_detailed_column_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get detailed statistics for each column.
        """
        stats = {}

        for col in df.columns:
            col_data = df[col]
            col_stats = {
                'name': col,
                'dtype': str(col_data.dtype),
                'count': int(col_data.count()),
                'null_count': int(col_data.isnull().sum()),
                'null_percentage': round((col_data.isnull().sum() / len(df)) * 100, 2),
                'unique_count': int(col_data.nunique()),
                'unique_percentage': round((col_data.nunique() / len(df)) * 100, 2)
            }

            if pd.api.types.is_numeric_dtype(col_data):
                col_stats.update({
                    'min': float(col_data.min()),
                    'max': float(col_data.max()),
                    'mean': round(float(col_data.mean()), 4),
                    'median': float(col_data.median()),
                    'std': round(float(col_data.std()), 4),
                    'q25': float(col_data.quantile(0.25)),
                    'q75': float(col_data.quantile(0.75))
                })

                # Detect outliers
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                outliers = col_data[(col_data < q1 - 1.5 * iqr) | (col_data > q3 + 1.5 * iqr)]
                col_stats['outlier_count'] = len(outliers)

            elif pd.api.types.is_datetime64_any_dtype(col_data):
                col_stats.update({
                    'min_date': str(col_data.min()),
                    'max_date': str(col_data.max()),
                    'date_range_days': (col_data.max() - col_data.min()).days
                })

            else:
                # String/object columns
                str_lengths = col_data.astype(str).str.len()
                col_stats.update({
                    'avg_length': round(float(str_lengths.mean()), 2),
                    'min_length': int(str_lengths.min()),
                    'max_length': int(str_lengths.max())
                })

            # Top values
            value_counts = col_data.value_counts().head(5)
            col_stats['top_values'] = [
                {'value': str(val), 'count': int(count)}
                for val, count in value_counts.items()
            ]

            stats[col] = col_stats

        return stats

    def _generate_visualization_suggestions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate visualization suggestions based on data types and characteristics.
        """
        suggestions = []

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

        # Histogram for numeric columns
        for col in numeric_cols[:5]:  # Limit to first 5
            suggestions.append({
                'type': 'histogram',
                'title': f'Distribution of {col}',
                'columns': [col],
                'description': f'Shows the frequency distribution of values in {col}',
                'chart_type': 'histogram'
            })

        # Bar chart for categorical columns with reasonable cardinality
        for col in categorical_cols[:3]:
            unique_count = df[col].nunique()
            if 2 <= unique_count <= 20:
                suggestions.append({
                    'type': 'bar_chart',
                    'title': f'Count by {col}',
                    'columns': [col],
                    'description': f'Shows the frequency of each category in {col}',
                    'chart_type': 'bar'
                })

        # Scatter plot for numeric pairs
        if len(numeric_cols) >= 2:
            suggestions.append({
                'type': 'scatter_plot',
                'title': f'{numeric_cols[0]} vs {numeric_cols[1]}',
                'columns': numeric_cols[:2],
                'description': f'Shows the relationship between {numeric_cols[0]} and {numeric_cols[1]}',
                'chart_type': 'scatter'
            })

        # Time series for datetime columns
        for col in datetime_cols[:2]:
            if len(numeric_cols) > 0:
                suggestions.append({
                    'type': 'line_chart',
                    'title': f'{numeric_cols[0]} over time',
                    'columns': [col, numeric_cols[0]],
                    'description': f'Shows how {numeric_cols[0]} changes over time',
                    'chart_type': 'line'
                })

        # Correlation heatmap if multiple numeric columns
        if len(numeric_cols) >= 3:
            suggestions.append({
                'type': 'heatmap',
                'title': 'Correlation Matrix',
                'columns': numeric_cols[:10],
                'description': 'Shows correlations between numeric variables',
                'chart_type': 'heatmap'
            })

        return suggestions

    def _identify_data_issues(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify potential data quality issues.
        """
        issues = []

        # Missing values
        missing_data = df.isnull().sum()
        for col, missing_count in missing_data.items():
            if missing_count > 0:
                percentage = (missing_count / len(df)) * 100
                severity = 'high' if percentage > 50 else 'medium' if percentage > 20 else 'low'
                issues.append({
                    'type': 'missing_values',
                    'column': col,
                    'severity': severity,
                    'count': int(missing_count),
                    'percentage': round(percentage, 2),
                    'description': f'{col} has {missing_count} missing values ({percentage:.1f}%)'
                })

        # Duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            issues.append({
                'type': 'duplicate_rows',
                'severity': 'medium',
                'count': int(duplicate_count),
                'percentage': round((duplicate_count / len(df)) * 100, 2),
                'description': f'Found {duplicate_count} duplicate rows'
            })

        # Columns with single value (no variance)
        for col in df.columns:
            if df[col].nunique() == 1:
                issues.append({
                    'type': 'no_variance',
                    'column': col,
                    'severity': 'low',
                    'description': f'{col} has only one unique value'
                })

        # High cardinality categorical columns
        for col in df.select_dtypes(include=['object']).columns:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio > 0.9:
                issues.append({
                    'type': 'high_cardinality',
                    'column': col,
                    'severity': 'medium',
                    'unique_count': int(df[col].nunique()),
                    'description': f'{col} has very high cardinality ({df[col].nunique()} unique values)'
                })

        # Potential outliers in numeric columns
        for col in df.select_dtypes(include=[np.number]).columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]

            if len(outliers) > 0:
                outlier_percentage = (len(outliers) / len(df)) * 100
                severity = 'high' if outlier_percentage > 10 else 'medium' if outlier_percentage > 5 else 'low'
                issues.append({
                    'type': 'outliers',
                    'column': col,
                    'severity': severity,
                    'count': len(outliers),
                    'percentage': round(outlier_percentage, 2),
                    'description': f'{col} has {len(outliers)} potential outliers ({outlier_percentage:.1f}%)'
                })

        return issues

    def _generate_data_recommendations(self, df: pd.DataFrame, ai_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations for data analysis.
        """
        recommendations = []

        # Basic recommendations based on data characteristics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns

        if len(numeric_cols) >= 2:
            recommendations.append(
                f"Explore correlations between numeric variables: {', '.join(numeric_cols[:5])}"
            )

        if len(categorical_cols) > 0:
            recommendations.append(
                f"Analyze distributions of categorical variables: {', '.join(categorical_cols[:3])}"
            )

        # Missing data recommendations
        missing_data = df.isnull().sum()
        high_missing = missing_data[missing_data > len(df) * 0.3]
        if len(high_missing) > 0:
            recommendations.append(
                f"Consider removing or imputing columns with high missing data: {', '.join(high_missing.index)}"
            )

        # Data size recommendations
        if len(df) > 100000:
            recommendations.append(
                "Consider sampling for initial exploration due to large dataset size"
            )

        if len(df.columns) > 20:
            recommendations.append(
                "Focus on key variables first - consider dimensionality reduction techniques"
            )

        # Specific analysis suggestions
        recommendations.extend([
            "Start with exploratory data analysis (EDA) to understand data distributions",
            "Check for data quality issues before proceeding with analysis",
            "Consider creating derived features from existing variables",
            "Document any data transformations for reproducibility"
        ])

        return recommendations


class DataAnalysisService:
    """
    Service for data analysis and quality assessment.
    """
    
    def analyze_data_source(self, data_source: DataSource, **options) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of data source.
        """
        try:
            # Read data
            ingestion_service = DataIngestionService()
            
            if data_source.source_type == 'file':
                df = ingestion_service.read_file_data(
                    data_source.file.path,
                    data_source.file_type
                )
            else:
                # For non-file sources, get preview data
                preview = ingestion_service.get_data_preview(
                    data_source,
                    limit=options.get('sample_size', 1000)
                )
                df = pd.DataFrame(preview['data'])
            
            analysis_result = {}
            
            # Basic statistics
            if options.get('include_column_analysis', True):
                analysis_result['column_analysis'] = self._analyze_columns(df)
            
            # Quality report
            if options.get('include_quality_report', True):
                quality_report = self.generate_quality_report(data_source, df)
                analysis_result['quality_report'] = quality_report
            
            # Sample data
            if options.get('include_sample_data', True):
                analysis_result['sample_data'] = df.head(10).to_dict('records')
            
            return analysis_result
        
        except Exception as e:
            logger.error(f"Error analyzing data source: {str(e)}")
            raise
    
    def generate_quality_report(self, data_source: DataSource, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate data quality report.
        """
        try:
            # Calculate quality scores
            total_cells = df.size
            null_cells = df.isnull().sum().sum()
            completeness_score = ((total_cells - null_cells) / total_cells) * 100
            
            # Detect issues
            issues = []
            
            # Missing values
            missing_cols = df.isnull().sum()
            for col, missing_count in missing_cols.items():
                if missing_count > 0:
                    percentage = (missing_count / len(df)) * 100
                    severity = 'high' if percentage > 50 else 'medium' if percentage > 20 else 'low'
                    issues.append({
                        'type': 'missing_values',
                        'column': col,
                        'severity': severity,
                        'description': f'{missing_count} missing values ({percentage:.1f}%)',
                        'count': int(missing_count)
                    })
            
            # Duplicate rows
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                issues.append({
                    'type': 'duplicate_rows',
                    'severity': 'medium',
                    'description': f'{duplicate_count} duplicate rows found',
                    'count': int(duplicate_count)
                })
            
            # Data type inconsistencies
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Check for mixed types
                    sample = df[col].dropna().head(100)
                    types = set(type(x).__name__ for x in sample)
                    if len(types) > 1:
                        issues.append({
                            'type': 'mixed_types',
                            'column': col,
                            'severity': 'medium',
                            'description': f'Mixed data types detected: {", ".join(types)}',
                            'types': list(types)
                        })
            
            # Calculate overall scores
            issue_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
            for issue in issues:
                issue_counts[issue['severity']] += 1
            
            # Overall quality score
            penalty = (issue_counts['critical'] * 20 + 
                      issue_counts['high'] * 10 + 
                      issue_counts['medium'] * 5 + 
                      issue_counts['low'] * 2)
            overall_score = max(0, 100 - penalty)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(issues)
            
            # Create or update quality report
            quality_report, created = DataQualityReport.objects.get_or_create(
                data_source=data_source,
                defaults={
                    'overall_score': overall_score,
                    'completeness_score': completeness_score,
                    'consistency_score': 85,  # Placeholder
                    'accuracy_score': 90,     # Placeholder
                    'validity_score': 88,     # Placeholder
                    'total_issues': len(issues),
                    'critical_issues': issue_counts['critical'],
                    'high_issues': issue_counts['high'],
                    'medium_issues': issue_counts['medium'],
                    'low_issues': issue_counts['low'],
                    'issues': issues,
                    'recommendations': recommendations,
                }
            )
            
            if not created:
                # Update existing report
                quality_report.overall_score = overall_score
                quality_report.completeness_score = completeness_score
                quality_report.total_issues = len(issues)
                quality_report.critical_issues = issue_counts['critical']
                quality_report.high_issues = issue_counts['high']
                quality_report.medium_issues = issue_counts['medium']
                quality_report.low_issues = issue_counts['low']
                quality_report.issues = issues
                quality_report.recommendations = recommendations
                quality_report.save()
            
            return {
                'overall_score': overall_score,
                'completeness_score': completeness_score,
                'total_issues': len(issues),
                'issues': issues,
                'recommendations': recommendations
            }
        
        except Exception as e:
            logger.error(f"Error generating quality report: {str(e)}")
            raise
    
    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze individual columns.
        """
        column_analysis = {}
        
        for column in df.columns:
            col_data = df[column]
            
            analysis = {
                'data_type': str(col_data.dtype),
                'null_count': int(col_data.isnull().sum()),
                'null_percentage': float((col_data.isnull().sum() / len(df)) * 100),
                'unique_count': int(col_data.nunique()),
                'unique_percentage': float((col_data.nunique() / len(df)) * 100),
            }
            
            # Type-specific analysis
            if pd.api.types.is_numeric_dtype(col_data):
                analysis.update({
                    'min_value': float(col_data.min()),
                    'max_value': float(col_data.max()),
                    'mean_value': float(col_data.mean()),
                    'median_value': float(col_data.median()),
                    'std_deviation': float(col_data.std()),
                })
            
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                analysis.update({
                    'min_date': str(col_data.min()),
                    'max_date': str(col_data.max()),
                })
            
            else:
                # String/object columns
                analysis.update({
                    'avg_length': float(col_data.astype(str).str.len().mean()),
                    'max_length': int(col_data.astype(str).str.len().max()),
                    'min_length': int(col_data.astype(str).str.len().min()),
                })
            
            column_analysis[column] = analysis
        
        return column_analysis
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        Generate recommendations based on detected issues.
        """
        recommendations = []
        
        # Group issues by type
        issue_types = {}
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        # Generate recommendations
        if 'missing_values' in issue_types:
            missing_issues = issue_types['missing_values']
            high_missing = [i for i in missing_issues if i['severity'] == 'high']
            if high_missing:
                recommendations.append(
                    f"Consider removing columns with >50% missing values: "
                    f"{', '.join([i['column'] for i in high_missing])}"
                )
            else:
                recommendations.append(
                    "Implement data validation rules to prevent missing values in critical columns"
                )
        
        if 'duplicate_rows' in issue_types:
            recommendations.append(
                "Remove duplicate rows to improve data quality and reduce storage costs"
            )
        
        if 'mixed_types' in issue_types:
            recommendations.append(
                "Standardize data types in columns with mixed types to improve consistency"
            )
        
        # General recommendations
        if len(issues) > 10:
            recommendations.append(
                "Consider implementing automated data quality checks in your data pipeline"
            )
        
        return recommendations
