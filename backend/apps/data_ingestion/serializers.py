"""
Serializers for data ingestion app.
"""

from rest_framework import serializers
from django.core.files.uploadedfile import UploadedFile
from .models import DataSource, DataColumn, DataQualityReport, DataTransformation


class DataColumnSerializer(serializers.ModelSerializer):
    """
    Serializer for data columns.
    """
    
    class Meta:
        model = DataColumn
        fields = [
            'id', 'name', 'original_name', 'data_type', 'is_nullable',
            'is_primary_key', 'is_foreign_key', 'null_count', 'unique_count',
            'min_value', 'max_value', 'mean_value', 'std_deviation',
            'quality_score', 'has_outliers', 'outlier_count',
            'description', 'sample_values', 'value_counts',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DataQualityReportSerializer(serializers.ModelSerializer):
    """
    Serializer for data quality reports.
    """
    
    class Meta:
        model = DataQualityReport
        fields = [
            'overall_score', 'completeness_score', 'consistency_score',
            'accuracy_score', 'validity_score', 'total_issues',
            'critical_issues', 'high_issues', 'medium_issues', 'low_issues',
            'issues', 'recommendations', 'generated_at', 'processing_time'
        ]
        read_only_fields = ['generated_at']


class DataTransformationSerializer(serializers.ModelSerializer):
    """
    Serializer for data transformations.
    """
    
    class Meta:
        model = DataTransformation
        fields = [
            'id', 'name', 'description', 'transformation_type', 'status',
            'operations', 'sql_query', 'python_code', 'output_rows',
            'output_columns', 'execution_time', 'error_message',
            'created_at', 'updated_at', 'executed_at'
        ]
        read_only_fields = [
            'id', 'status', 'output_rows', 'output_columns',
            'execution_time', 'error_message', 'created_at',
            'updated_at', 'executed_at'
        ]


class DataSourceSerializer(serializers.ModelSerializer):
    """
    Serializer for data sources.
    """
    columns = DataColumnSerializer(many=True, read_only=True)
    quality_report = DataQualityReportSerializer(read_only=True)
    transformations = DataTransformationSerializer(many=True, read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    
    class Meta:
        model = DataSource
        fields = [
            'id', 'name', 'description', 'source_type', 'status',
            'file', 'file_size', 'file_size_mb', 'file_type',
            'db_type', 'db_host', 'db_port', 'db_name', 'db_username',
            'db_table', 'db_query', 'api_url', 'api_method', 'api_headers',
            'api_params', 'api_auth_type', 'rows_count', 'columns_count',
            'processing_time', 'error_message', 'created_at', 'updated_at',
            'processed_at', 'is_public', 'auto_refresh', 'refresh_interval',
            'columns', 'quality_report', 'transformations'
        ]
        read_only_fields = [
            'id', 'status', 'file_size', 'file_type', 'rows_count',
            'columns_count', 'processing_time', 'error_message',
            'created_at', 'updated_at', 'processed_at'
        ]
        extra_kwargs = {
            'db_password': {'write_only': True},
            'api_auth_token': {'write_only': True},
        }

    def validate_file(self, value):
        """Validate uploaded file."""
        if value:
            # Check file size (100MB limit)
            if value.size > 100 * 1024 * 1024:
                raise serializers.ValidationError(
                    "File size cannot exceed 100MB."
                )
            
            # Check file extension
            allowed_extensions = ['csv', 'xlsx', 'xls', 'json', 'parquet']
            file_extension = value.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise serializers.ValidationError(
                    f"File type '{file_extension}' is not supported. "
                    f"Allowed types: {', '.join(allowed_extensions)}"
                )
        
        return value

    def validate(self, attrs):
        """Validate data source configuration."""
        source_type = attrs.get('source_type')
        
        if source_type == 'file':
            if not attrs.get('file'):
                raise serializers.ValidationError(
                    "File is required for file-type data sources."
                )
        
        elif source_type == 'database':
            required_fields = ['db_type', 'db_host', 'db_name', 'db_username']
            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError(
                        f"{field} is required for database connections."
                    )
        
        elif source_type == 'api':
            if not attrs.get('api_url'):
                raise serializers.ValidationError(
                    "API URL is required for API data sources."
                )
        
        return attrs


class DataSourceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating data sources.
    """
    
    class Meta:
        model = DataSource
        fields = [
            'name', 'description', 'source_type', 'file',
            'db_type', 'db_host', 'db_port', 'db_name',
            'db_username', 'db_password', 'db_table', 'db_query',
            'api_url', 'api_method', 'api_headers', 'api_params',
            'api_auth_type', 'api_auth_token', 'is_public',
            'auto_refresh', 'refresh_interval'
        ]
        extra_kwargs = {
            'db_password': {'write_only': True},
            'api_auth_token': {'write_only': True},
        }


class DataSourceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating data sources.
    """
    
    class Meta:
        model = DataSource
        fields = [
            'name', 'description', 'is_public', 'auto_refresh', 'refresh_interval'
        ]


class FileUploadSerializer(serializers.Serializer):
    """
    Serializer for file uploads.
    """
    file = serializers.FileField()
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False)
    
    def validate_file(self, value):
        """Validate uploaded file."""
        # Check file size (100MB limit)
        if value.size > 100 * 1024 * 1024:
            raise serializers.ValidationError(
                "File size cannot exceed 100MB."
            )
        
        # Check file extension
        allowed_extensions = ['csv', 'xlsx', 'xls', 'json', 'parquet']
        file_extension = value.name.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type '{file_extension}' is not supported. "
                f"Allowed types: {', '.join(allowed_extensions)}"
            )
        
        return value


class DataPreviewSerializer(serializers.Serializer):
    """
    Serializer for data preview requests.
    """
    limit = serializers.IntegerField(default=100, min_value=1, max_value=1000)
    offset = serializers.IntegerField(default=0, min_value=0)
    columns = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of column names to include in preview"
    )
    filters = serializers.DictField(
        required=False,
        help_text="Dictionary of column filters"
    )


class DataAnalysisSerializer(serializers.Serializer):
    """
    Serializer for data analysis requests.
    """
    include_quality_report = serializers.BooleanField(default=True)
    include_column_analysis = serializers.BooleanField(default=True)
    include_sample_data = serializers.BooleanField(default=True)
    sample_size = serializers.IntegerField(default=1000, min_value=100, max_value=10000)


class DatabaseConnectionSerializer(serializers.Serializer):
    """
    Serializer for testing database connections.
    """
    db_type = serializers.ChoiceField(choices=[
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('sqlite', 'SQLite'),
        ('oracle', 'Oracle'),
        ('mssql', 'SQL Server'),
    ])
    db_host = serializers.CharField(max_length=255)
    db_port = serializers.IntegerField(min_value=1, max_value=65535)
    db_name = serializers.CharField(max_length=255)
    db_username = serializers.CharField(max_length=255)
    db_password = serializers.CharField(max_length=255, write_only=True)
    
    def validate(self, attrs):
        """Validate database connection parameters."""
        # Add any database-specific validation here
        return attrs


class APIConnectionSerializer(serializers.Serializer):
    """
    Serializer for testing API connections.
    """
    api_url = serializers.URLField()
    api_method = serializers.ChoiceField(
        choices=['GET', 'POST', 'PUT', 'PATCH'],
        default='GET'
    )
    api_headers = serializers.DictField(required=False)
    api_params = serializers.DictField(required=False)
    api_auth_type = serializers.ChoiceField(
        choices=[
            ('none', 'None'),
            ('bearer', 'Bearer Token'),
            ('basic', 'Basic Auth'),
            ('api_key', 'API Key'),
        ],
        default='none'
    )
    api_auth_token = serializers.CharField(required=False, write_only=True)
