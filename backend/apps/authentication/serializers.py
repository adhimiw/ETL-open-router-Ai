"""
Serializers for authentication app.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, APIKey


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'organization', 'role'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Invalid email or password.'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.'
                )
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError(
            'Must include email and password.'
        )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'organization', 'phone_number',
            'profile_picture', 'preferred_language', 'timezone',
            'api_calls_count', 'data_processed_mb', 'is_verified',
            'created_at', 'last_login'
        ]
        read_only_fields = [
            'id', 'username', 'email', 'role', 'api_calls_count',
            'data_processed_mb', 'is_verified', 'created_at', 'last_login'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class APIKeySerializer(serializers.ModelSerializer):
    """
    Serializer for API keys.
    """
    key = serializers.CharField(read_only=True)
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key', 'is_active', 'created_at',
            'last_used', 'usage_count', 'rate_limit_per_hour',
            'rate_limit_per_day'
        ]
        read_only_fields = [
            'id', 'key', 'created_at', 'last_used', 'usage_count'
        ]


class UserStatsSerializer(serializers.Serializer):
    """
    Serializer for user statistics.
    """
    total_api_calls = serializers.IntegerField()
    total_data_processed_mb = serializers.FloatField()
    active_sessions = serializers.IntegerField()
    api_keys_count = serializers.IntegerField()
    last_login = serializers.DateTimeField()
    account_age_days = serializers.IntegerField()
