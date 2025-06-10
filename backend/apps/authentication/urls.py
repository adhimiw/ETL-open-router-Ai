"""
URL configuration for authentication app.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # API Keys
    path('api-keys/', views.APIKeyListCreateView.as_view(), name='api_keys'),
    path('api-keys/<int:pk>/', views.APIKeyDetailView.as_view(), name='api_key_detail'),
    
    # User statistics and sessions
    path('stats/', views.UserStatsView.as_view(), name='user_stats'),
    path('sessions/', views.user_sessions, name='user_sessions'),
    path('sessions/<int:session_id>/terminate/', views.terminate_session, name='terminate_session'),
]
