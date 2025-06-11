"""
URL configuration for Query Processor app.
"""
from django.urls import path
from . import views

app_name = 'query_processor'

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health_check'),

    # Query processing
    path('process/', views.process_query, name='process_query'),
    path('generate-sql/', views.generate_sql, name='generate_sql'),
    path('generate-python/', views.generate_python, name='generate_python'),

    # Query history
    path('history/', views.query_history, name='query_history'),
]
