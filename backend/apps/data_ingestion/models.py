"""
Data ingestion models for EETL AI Platform.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
import uuid
import os

User = get_user_model()


def upload_to(instance, filename):
    """Generate upload path for data files."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', str(instance.user.id), filename)


class DataSource(models.Model):
    """
    Model for different data sources (files, databases, APIs).
    """
    
    class SourceType(models.TextChoices):
        FILE = 'file', 'File Upload'
        DATABASE = 'database', 'Database Connection'
        API = 'api', 'API Endpoint'
        URL = 'url', 'URL/Web Scraping'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        ARCHIVED = 'archived', 'Archived'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_sources')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # File upload fields
    file = models.FileField(
        upload_to=upload_to,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xlsx', 'xls', 'json', 'parquet'])]
    )
    file_size = models.BigIntegerField(blank=True, null=True)  # in bytes
    file_type = models.CharField(max_length=50, blank=True, null=True)
    
    # Database connection fields
    db_type = models.CharField(max_length=50, blank=True, null=True)  # postgresql, mysql, sqlite, etc.
    db_host = models.CharField(max_length=255, blank=True, null=True)
    db_port = models.IntegerField(blank=True, null=True)
    db_name = models.CharField(max_length=255, blank=True, null=True)
    db_username = models.CharField(max_length=255, blank=True, null=True)
    db_password = models.CharField(max_length=255, blank=True, null=True)  # Should be encrypted
    db_table = models.CharField(max_length=255, blank=True, null=True)
    db_query = models.TextField(blank=True, null=True)
    
    # API endpoint fields
    api_url = models.URLField(blank=True, null=True)
    api_method = models.CharField(max_length=10, default='GET', blank=True, null=True)
    api_headers = models.JSONField(blank=True, null=True)
    api_params = models.JSONField(blank=True, null=True)
    api_auth_type = models.CharField(max_length=50, blank=True, null=True)
    api_auth_token = models.TextField(blank=True, null=True)
    
    # Processing metadata
    rows_count = models.BigIntegerField(blank=True, null=True)
    columns_count = models.IntegerField(blank=True, null=True)
    processing_time = models.FloatField(blank=True, null=True)  # in seconds
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    # Settings
    is_public = models.BooleanField(default=False)
    auto_refresh = models.BooleanField(default=False)
    refresh_interval = models.IntegerField(default=3600)  # in seconds
    
    class Meta:
        db_table = 'data_sources'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"
    
    @property
    def file_size_mb(self):
        """Return file size in MB."""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0


class DataColumn(models.Model):
    """
    Model for storing column metadata and statistics.
    """
    
    class DataType(models.TextChoices):
        STRING = 'string', 'String/Text'
        INTEGER = 'integer', 'Integer'
        FLOAT = 'float', 'Float/Decimal'
        BOOLEAN = 'boolean', 'Boolean'
        DATE = 'date', 'Date'
        DATETIME = 'datetime', 'DateTime'
        JSON = 'json', 'JSON'
        ARRAY = 'array', 'Array'
    
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)  # Original column name before cleaning
    data_type = models.CharField(max_length=20, choices=DataType.choices)
    is_nullable = models.BooleanField(default=True)
    is_primary_key = models.BooleanField(default=False)
    is_foreign_key = models.BooleanField(default=False)
    
    # Statistics
    null_count = models.BigIntegerField(default=0)
    unique_count = models.BigIntegerField(default=0)
    min_value = models.TextField(blank=True, null=True)
    max_value = models.TextField(blank=True, null=True)
    mean_value = models.FloatField(blank=True, null=True)
    std_deviation = models.FloatField(blank=True, null=True)
    
    # Data quality
    quality_score = models.FloatField(default=0.0)  # 0-100
    has_outliers = models.BooleanField(default=False)
    outlier_count = models.IntegerField(default=0)
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    sample_values = models.JSONField(blank=True, null=True)  # Array of sample values
    value_counts = models.JSONField(blank=True, null=True)  # Top value frequencies
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_columns'
        unique_together = ['data_source', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.data_source.name}.{self.name} ({self.get_data_type_display()})"


class DataQualityReport(models.Model):
    """
    Model for storing data quality assessment reports.
    """
    
    class Severity(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'
    
    data_source = models.OneToOneField(
        DataSource,
        on_delete=models.CASCADE,
        related_name='quality_report'
    )
    
    # Overall scores
    overall_score = models.FloatField(default=0.0)  # 0-100
    completeness_score = models.FloatField(default=0.0)
    consistency_score = models.FloatField(default=0.0)
    accuracy_score = models.FloatField(default=0.0)
    validity_score = models.FloatField(default=0.0)
    
    # Issue counts
    total_issues = models.IntegerField(default=0)
    critical_issues = models.IntegerField(default=0)
    high_issues = models.IntegerField(default=0)
    medium_issues = models.IntegerField(default=0)
    low_issues = models.IntegerField(default=0)
    
    # Detailed findings
    issues = models.JSONField(default=list)  # List of issue objects
    recommendations = models.JSONField(default=list)  # List of recommendations
    
    # Processing info
    generated_at = models.DateTimeField(auto_now_add=True)
    processing_time = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'data_quality_reports'
    
    def __str__(self):
        return f"Quality Report for {self.data_source.name} (Score: {self.overall_score})"


class DataTransformation(models.Model):
    """
    Model for storing data transformation operations.
    """
    
    class TransformationType(models.TextChoices):
        CLEAN = 'clean', 'Data Cleaning'
        FILTER = 'filter', 'Data Filtering'
        AGGREGATE = 'aggregate', 'Data Aggregation'
        JOIN = 'join', 'Data Joining'
        PIVOT = 'pivot', 'Data Pivoting'
        CUSTOM = 'custom', 'Custom Transformation'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.CASCADE,
        related_name='transformations'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    transformation_type = models.CharField(
        max_length=20,
        choices=TransformationType.choices
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Transformation definition
    operations = models.JSONField(default=list)  # List of transformation operations
    sql_query = models.TextField(blank=True, null=True)  # Generated SQL
    python_code = models.TextField(blank=True, null=True)  # Generated Python code
    
    # Results
    output_rows = models.BigIntegerField(blank=True, null=True)
    output_columns = models.IntegerField(blank=True, null=True)
    execution_time = models.FloatField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    executed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'data_transformations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_transformation_type_display()}"


class ETLOperation(models.Model):
    """
    Model for tracking ETL operations and their status.
    """

    class OperationType(models.TextChoices):
        DATA_INGESTION = 'data_ingestion', 'Data Ingestion'
        DATA_TRANSFORMATION = 'data_transformation', 'Data Transformation'
        DATA_EXPORT = 'data_export', 'Data Export'
        DATA_ANALYSIS = 'data_analysis', 'Data Analysis'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='etl_operations')
    operation_type = models.CharField(max_length=30, choices=OperationType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # Operation details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    progress = models.IntegerField(default=0)  # 0-100

    # Related objects
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='operations'
    )
    transformation = models.ForeignKey(
        DataTransformation,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='etl_operations'
    )

    # Execution details
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    execution_time = models.FloatField(blank=True, null=True)  # in seconds

    # Results and logs
    result_data = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    log_messages = models.JSONField(default=list)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'etl_operations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_operation_type_display()}) - {self.get_status_display()}"
