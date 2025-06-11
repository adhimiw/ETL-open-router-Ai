"""
URL configuration for AI Engine app.
"""
from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    # AI Engine endpoints will be added here
    path('health/', views.health_check, name='health_check'),
    path('conversations/', views.conversations, name='conversations'),
    path('conversations/<str:conversation_id>/messages/', views.conversation_messages, name='conversation_messages'),
    path('test-chat/', views.test_ai_chat, name='test_ai_chat'),
]
