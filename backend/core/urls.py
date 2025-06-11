"""
URL configuration for EETL AI Platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for BrowserMCP connection."""
    return Response({
        'status': 'healthy',
        'service': 'EETL AI Platform Backend',
        'version': '1.0.0',
        'timestamp': '2024-01-01T00:00:00Z'
    })

urlpatterns = [
    # Health Check
    path('api/health/', health_check, name='health_check'),

    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API Endpoints
    path('api/auth/', include('apps.authentication.urls')),
    path('api/data/', include('apps.data_ingestion.urls')),
    path('api/ai/', include('apps.ai_engine.urls')),
    path('api/query/', include('apps.query_processor.urls')),
    path('api/viz/', include('apps.visualization.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
