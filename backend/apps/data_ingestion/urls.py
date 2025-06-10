"""
URL configuration for data ingestion app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sources', views.DataSourceViewSet, basename='datasource')
router.register(r'transformations', views.DataTransformationViewSet, basename='transformation')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # File upload
    path('upload/', views.upload_file, name='upload_file'),
    
    # Connection testing
    path('test-database/', views.test_database_connection, name='test_database'),
    path('test-api/', views.test_api_connection, name='test_api'),
    
    # Utility endpoints
    path('formats/', views.get_supported_formats, name='supported_formats'),
    path('stats/', views.get_user_stats, name='user_stats'),
]
