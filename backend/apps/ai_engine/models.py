"""
AI Engine models for EETL AI Platform.
"""

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Conversation(models.Model):
    """
    Model for storing AI conversations with users.
    """
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'
        DELETED = 'deleted', 'Deleted'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    # Context
    data_source_id = models.UUIDField(blank=True, null=True)  # Reference to data source
    context_summary = models.TextField(blank=True, null=True)
    
    # Metadata
    message_count = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_conversations'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"Conversation {self.id} - {self.user.email}"
    
    def increment_message_count(self):
        """Increment message count."""
        self.message_count += 1
        self.save(update_fields=['message_count', 'updated_at'])


class Message(models.Model):
    """
    Model for storing individual messages in conversations.
    """
    
    class Role(models.TextChoices):
        USER = 'user', 'User'
        ASSISTANT = 'assistant', 'Assistant'
        SYSTEM = 'system', 'System'
    
    class MessageType(models.TextChoices):
        TEXT = 'text', 'Text'
        CODE = 'code', 'Code'
        QUERY = 'query', 'Query'
        VISUALIZATION = 'visualization', 'Visualization'
        FILE = 'file', 'File'
        ERROR = 'error', 'Error'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    message_type = models.CharField(max_length=20, choices=MessageType.choices, default=MessageType.TEXT)
    
    # Content
    content = models.TextField()
    metadata = models.JSONField(default=dict)  # Additional message metadata
    
    # AI processing
    tokens_used = models.IntegerField(default=0)
    processing_time = models.FloatField(default=0.0)  # in seconds
    model_used = models.CharField(max_length=100, blank=True, null=True)
    
    # Code execution (if applicable)
    code_language = models.CharField(max_length=50, blank=True, null=True)
    code_output = models.TextField(blank=True, null=True)
    execution_status = models.CharField(max_length=20, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role} message in {self.conversation.id}"


class AIModel(models.Model):
    """
    Model for tracking AI model configurations and usage.
    """
    
    class Provider(models.TextChoices):
        OPENROUTER = 'openrouter', 'OpenRouter'
        OPENAI = 'openai', 'OpenAI'
        ANTHROPIC = 'anthropic', 'Anthropic'
        HUGGINGFACE = 'huggingface', 'Hugging Face'
    
    name = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=20, choices=Provider.choices)
    model_id = models.CharField(max_length=100)  # e.g., "deepseek/deepseek-chat"
    
    # Capabilities
    supports_function_calling = models.BooleanField(default=False)
    supports_vision = models.BooleanField(default=False)
    supports_code_execution = models.BooleanField(default=False)
    max_tokens = models.IntegerField(default=4096)
    context_window = models.IntegerField(default=4096)
    
    # Pricing (per 1K tokens)
    input_price = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    output_price = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    
    # Usage tracking
    total_requests = models.BigIntegerField(default=0)
    total_tokens = models.BigIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_models'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.provider})"
    
    def increment_usage(self, tokens_used, cost=0.0):
        """Increment usage statistics."""
        self.total_requests += 1
        self.total_tokens += tokens_used
        self.total_cost += cost
        self.save(update_fields=['total_requests', 'total_tokens', 'total_cost'])


class EmbeddingModel(models.Model):
    """
    Model for embedding models used in RAG.
    """
    name = models.CharField(max_length=100, unique=True)
    model_id = models.CharField(max_length=100)
    dimensions = models.IntegerField()
    max_sequence_length = models.IntegerField(default=512)
    
    # Performance metrics
    avg_embedding_time = models.FloatField(default=0.0)
    total_embeddings = models.BigIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'embedding_models'
    
    def __str__(self):
        return f"{self.name} ({self.dimensions}d)"


class VectorStore(models.Model):
    """
    Model for tracking vector store collections.
    """
    
    class Status(models.TextChoices):
        BUILDING = 'building', 'Building'
        READY = 'ready', 'Ready'
        UPDATING = 'updating', 'Updating'
        ERROR = 'error', 'Error'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    collection_name = models.CharField(max_length=255, unique=True)
    
    # Associated data
    data_source_id = models.UUIDField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vector_stores')
    embedding_model = models.ForeignKey(EmbeddingModel, on_delete=models.CASCADE)
    
    # Metadata
    document_count = models.IntegerField(default=0)
    chunk_size = models.IntegerField(default=1000)
    chunk_overlap = models.IntegerField(default=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BUILDING)
    
    # Performance
    build_time = models.FloatField(default=0.0)
    last_query_time = models.FloatField(default=0.0)
    total_queries = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vector_stores'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Vector Store: {self.name}"


class QueryExecution(models.Model):
    """
    Model for tracking query executions and results.
    """
    
    class QueryType(models.TextChoices):
        NATURAL_LANGUAGE = 'natural_language', 'Natural Language'
        SQL = 'sql', 'SQL Query'
        PYTHON = 'python', 'Python Code'
        VISUALIZATION = 'visualization', 'Visualization'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='query_executions')
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='query_executions',
        blank=True,
        null=True
    )
    
    # Query details
    query_type = models.CharField(max_length=20, choices=QueryType.choices)
    original_query = models.TextField()  # User's natural language query
    generated_code = models.TextField(blank=True, null=True)  # Generated SQL/Python
    
    # Execution
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    execution_time = models.FloatField(default=0.0)
    rows_affected = models.IntegerField(default=0)
    
    # Results
    result_data = models.JSONField(blank=True, null=True)  # Query results
    result_summary = models.TextField(blank=True, null=True)  # AI-generated summary
    error_message = models.TextField(blank=True, null=True)
    
    # AI processing
    ai_model_used = models.ForeignKey(
        AIModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    tokens_used = models.IntegerField(default=0)
    ai_processing_time = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'query_executions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Query {self.id} - {self.query_type}"
