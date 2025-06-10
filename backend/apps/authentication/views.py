"""
Authentication views for EETL AI Platform.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login, logout
from django.utils import timezone
from datetime import timedelta
import secrets

from .models import User, APIKey, UserSession
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    APIKeySerializer,
    UserStatsSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    User login endpoint with session tracking.
    """
    
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Update last login
        user.last_login = timezone.now()
        user.last_login_ip = self.get_client_ip(request)
        user.save(update_fields=['last_login', 'last_login_ip'])
        
        # Create session record
        UserSession.objects.create(
            user=user,
            session_key=request.session.session_key or 'api_access',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful'
        })
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(APIView):
    """
    User logout endpoint.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Deactivate session
            UserSession.objects.filter(
                user=request.user,
                is_active=True
            ).update(is_active=False)
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view and update.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    Change user password.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password changed successfully'
        })


class APIKeyListCreateView(generics.ListCreateAPIView):
    """
    List and create API keys.
    """
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Generate secure API key
        api_key = secrets.token_urlsafe(32)
        serializer.save(user=self.request.user, key=api_key)


class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete API key.
    """
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)


class UserStatsView(APIView):
    """
    Get user statistics and usage data.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Calculate statistics
        active_sessions = UserSession.objects.filter(
            user=user,
            is_active=True,
            last_activity__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        api_keys_count = APIKey.objects.filter(
            user=user,
            is_active=True
        ).count()
        
        account_age = (timezone.now() - user.created_at).days
        
        stats_data = {
            'total_api_calls': user.api_calls_count,
            'total_data_processed_mb': user.data_processed_mb,
            'active_sessions': active_sessions,
            'api_keys_count': api_keys_count,
            'last_login': user.last_login,
            'account_age_days': account_age
        }
        
        serializer = UserStatsSerializer(stats_data)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_sessions(request):
    """
    Get user's active sessions.
    """
    sessions = UserSession.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-last_activity')[:10]
    
    sessions_data = []
    for session in sessions:
        sessions_data.append({
            'id': session.id,
            'ip_address': session.ip_address,
            'user_agent': session.user_agent,
            'created_at': session.created_at,
            'last_activity': session.last_activity,
            'is_current': session.session_key == request.session.session_key
        })
    
    return Response(sessions_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def terminate_session(request, session_id):
    """
    Terminate a specific user session.
    """
    try:
        session = UserSession.objects.get(
            id=session_id,
            user=request.user
        )
        session.is_active = False
        session.save()
        
        return Response({
            'message': 'Session terminated successfully'
        })
    except UserSession.DoesNotExist:
        return Response({
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)
