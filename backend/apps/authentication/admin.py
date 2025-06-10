"""
Admin configuration for authentication app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserSession, APIKey


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model.
    """
    list_display = [
        'email', 'username', 'first_name', 'last_name',
        'role', 'organization', 'is_active', 'is_verified',
        'api_calls_count', 'created_at'
    ]
    list_filter = [
        'role', 'is_active', 'is_verified', 'is_staff',
        'created_at', 'last_login'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'organization']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': (
                'role', 'organization', 'phone_number',
                'profile_picture', 'preferred_language', 'timezone'
            )
        }),
        ('Usage Statistics', {
            'fields': (
                'api_calls_count', 'data_processed_mb',
                'last_login_ip'
            )
        }),
        ('Account Status', {
            'fields': (
                'is_verified', 'verification_token'
            )
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login_ip']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for UserSession model.
    """
    list_display = [
        'user', 'ip_address', 'is_active',
        'created_at', 'last_activity'
    ]
    list_filter = ['is_active', 'created_at', 'last_activity']
    search_fields = ['user__email', 'ip_address']
    ordering = ['-last_activity']
    readonly_fields = ['session_key', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """
    Admin interface for APIKey model.
    """
    list_display = [
        'user', 'name', 'is_active', 'usage_count',
        'rate_limit_per_hour', 'created_at', 'last_used'
    ]
    list_filter = ['is_active', 'created_at', 'last_used']
    search_fields = ['user__email', 'name']
    ordering = ['-created_at']
    readonly_fields = ['key', 'created_at', 'last_used', 'usage_count']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
