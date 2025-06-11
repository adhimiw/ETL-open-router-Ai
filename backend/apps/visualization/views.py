"""
Views for Visualization app.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for Visualization."""
    return Response({
        'status': 'healthy',
        'service': 'Visualization',
        'version': '1.0.0'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_chart_config(request):
    """Generate chart configuration based on data and user preferences."""
    try:
        data = request.data.get('data', [])
        chart_type = request.data.get('chart_type', 'bar')
        x_column = request.data.get('x_column')
        y_column = request.data.get('y_column')

        if not data:
            return Response({
                'status': 'error',
                'message': 'Data is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Convert data to DataFrame for analysis
        df = pd.DataFrame(data)

        # Auto-detect columns if not provided
        if not x_column or not y_column:
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            text_columns = df.select_dtypes(include=['object']).columns.tolist()

            if not x_column:
                x_column = text_columns[0] if text_columns else numeric_columns[0] if numeric_columns else df.columns[0]
            if not y_column:
                y_column = numeric_columns[0] if numeric_columns else df.columns[1] if len(df.columns) > 1 else df.columns[0]

        # Generate chart configuration
        chart_config = {
            'type': chart_type,
            'data': data,
            'config': {
                'x_axis': x_column,
                'y_axis': y_column,
                'title': f'{chart_type.title()} Chart: {y_column} by {x_column}',
                'x_label': x_column.replace('_', ' ').title(),
                'y_label': y_column.replace('_', ' ').title()
            }
        }

        # Add chart-specific configurations
        if chart_type == 'pie':
            # For pie charts, aggregate data by x_column
            aggregated = df.groupby(x_column)[y_column].sum().reset_index()
            chart_config['data'] = aggregated.to_dict('records')
            chart_config['config']['value_column'] = y_column
            chart_config['config']['label_column'] = x_column

        elif chart_type == 'line':
            # For line charts, ensure data is sorted by x_column
            sorted_df = df.sort_values(x_column)
            chart_config['data'] = sorted_df.to_dict('records')

        elif chart_type == 'scatter':
            # For scatter plots, we need both numeric columns
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_columns) >= 2:
                chart_config['config']['x_axis'] = numeric_columns[0]
                chart_config['config']['y_axis'] = numeric_columns[1]

        # Add summary statistics
        chart_config['stats'] = {
            'total_records': len(df),
            'columns': list(df.columns),
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'text_columns': df.select_dtypes(include=['object']).columns.tolist()
        }

        return Response(chart_config)

    except Exception as e:
        logger.error(f"Chart configuration error: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'Failed to generate chart configuration: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def suggest_visualizations(request):
    """Suggest appropriate visualizations based on data characteristics."""
    try:
        data = request.data.get('data', [])

        if not data:
            return Response({
                'status': 'error',
                'message': 'Data is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Convert data to DataFrame for analysis
        df = pd.DataFrame(data)

        # Analyze data characteristics
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        text_columns = df.select_dtypes(include=['object']).columns.tolist()
        date_columns = df.select_dtypes(include=['datetime']).columns.tolist()

        suggestions = []

        # Bar chart suggestions
        if text_columns and numeric_columns:
            suggestions.append({
                'type': 'bar',
                'title': 'Bar Chart',
                'description': f'Compare {numeric_columns[0]} across {text_columns[0]}',
                'x_column': text_columns[0],
                'y_column': numeric_columns[0],
                'suitability': 'high'
            })

        # Line chart suggestions
        if date_columns and numeric_columns:
            suggestions.append({
                'type': 'line',
                'title': 'Line Chart',
                'description': f'Show {numeric_columns[0]} trends over time',
                'x_column': date_columns[0],
                'y_column': numeric_columns[0],
                'suitability': 'high'
            })
        elif len(numeric_columns) >= 2:
            suggestions.append({
                'type': 'line',
                'title': 'Line Chart',
                'description': f'Show relationship between {numeric_columns[0]} and {numeric_columns[1]}',
                'x_column': numeric_columns[0],
                'y_column': numeric_columns[1],
                'suitability': 'medium'
            })

        # Pie chart suggestions
        if text_columns and numeric_columns:
            # Check if text column has reasonable number of unique values for pie chart
            unique_values = df[text_columns[0]].nunique()
            if unique_values <= 10:
                suggestions.append({
                    'type': 'pie',
                    'title': 'Pie Chart',
                    'description': f'Show distribution of {numeric_columns[0]} by {text_columns[0]}',
                    'x_column': text_columns[0],
                    'y_column': numeric_columns[0],
                    'suitability': 'high' if unique_values <= 6 else 'medium'
                })

        # Scatter plot suggestions
        if len(numeric_columns) >= 2:
            suggestions.append({
                'type': 'scatter',
                'title': 'Scatter Plot',
                'description': f'Explore correlation between {numeric_columns[0]} and {numeric_columns[1]}',
                'x_column': numeric_columns[0],
                'y_column': numeric_columns[1],
                'suitability': 'high'
            })

        # Table suggestion (always available)
        suggestions.append({
            'type': 'table',
            'title': 'Data Table',
            'description': 'View raw data in tabular format',
            'suitability': 'high'
        })

        return Response({
            'suggestions': suggestions,
            'data_analysis': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'numeric_columns': len(numeric_columns),
                'text_columns': len(text_columns),
                'date_columns': len(date_columns),
                'column_details': {
                    'numeric': numeric_columns,
                    'text': text_columns,
                    'date': date_columns
                }
            }
        })

    except Exception as e:
        logger.error(f"Visualization suggestion error: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'Failed to suggest visualizations: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
