"""
URL configuration for Visualization app.
"""
from django.urls import path
from . import views

app_name = 'visualization'

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health_check'),

    # Chart generation
    path('chart-config/', views.generate_chart_config, name='generate_chart_config'),
    path('suggestions/', views.suggest_visualizations, name='suggest_visualizations'),
]
