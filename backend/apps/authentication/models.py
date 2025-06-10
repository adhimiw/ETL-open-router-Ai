"""
Authentication models for EETL AI Platform.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Extended User model with additional fields for EETL platform.
    """
    
    class UserRole(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        DEVELOPER = 'developer', 'Developer'
        ANALYST = 'analyst', 'Business Analyst'
        PUBLIC = 'public', 'Public User'
    
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PUBLIC
    )
    organization = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Usage tracking
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    api_calls_count = models.PositiveIntegerField(default=0)
    data_processed_mb = models.FloatField(default=0.0)
    
    # Account status
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def increment_api_calls(self):
        """Increment API calls counter."""
        self.api_calls_count += 1
        self.save(update_fields=['api_calls_count'])
    
    def add_data_processed(self, mb_size):
        """Add to data processed counter."""
        self.data_processed_mb += mb_size
        self.save(update_fields=['data_processed_mb'])


class UserSession(models.Model):
    """
    Track user sessions for analytics and security.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"


class APIKey(models.Model):
    """
    API keys for programmatic access.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(blank=True, null=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Rate limiting
    rate_limit_per_hour = models.PositiveIntegerField(default=1000)
    rate_limit_per_day = models.PositiveIntegerField(default=10000)
    
    class Meta:
        db_table = 'api_keys'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"
    
    def increment_usage(self):
        """Increment usage counter and update last used."""
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])
