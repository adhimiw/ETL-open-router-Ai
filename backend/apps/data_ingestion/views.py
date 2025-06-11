"""
Views for data ingestion app.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db import transaction
import pandas as pd
import json

from .models import DataSource, DataColumn, DataQualityReport, DataTransformation, ETLOperation
from .serializers import (
    DataSourceSerializer,
    DataSourceCreateSerializer,
    DataSourceUpdateSerializer,
    FileUploadSerializer,
    DataPreviewSerializer,
    DataAnalysisSerializer,
    DatabaseConnectionSerializer,
    APIConnectionSerializer,
    DataColumnSerializer,
    DataQualityReportSerializer,
    DataTransformationSerializer,
    ETLOperationSerializer,
)
from .services import DataIngestionService, DataAnalysisService


class DataSourceViewSet(ModelViewSet):
    """
    ViewSet for managing data sources.
    """
    permission_classes = [permissions.AllowAny]  # Temporarily allow unauthenticated access
    
    def get_queryset(self):
        # For development, return all data sources if user is not authenticated
        if self.request.user.is_authenticated:
            return DataSource.objects.filter(user=self.request.user).order_by('-created_at')
        else:
            return DataSource.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DataSourceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DataSourceUpdateSerializer
        return DataSourceSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """
        Trigger data analysis for a data source.
        """
        data_source = self.get_object()
        serializer = DataAnalysisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            analysis_service = DataAnalysisService()
            result = analysis_service.analyze_data_source(
                data_source,
                **serializer.validated_data
            )
            
            return Response({
                'message': 'Analysis completed successfully',
                'analysis': result
            })
        
        except Exception as e:
            return Response(
                {'error': f'Analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Get data preview for a data source.
        """
        data_source = self.get_object()
        serializer = DataPreviewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        try:
            ingestion_service = DataIngestionService()
            preview_data = ingestion_service.get_data_preview(
                data_source,
                **serializer.validated_data
            )
            
            return Response(preview_data)
        
        except Exception as e:
            return Response(
                {'error': f'Preview failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def columns(self, request, pk=None):
        """
        Get column information for a data source.
        """
        data_source = self.get_object()
        columns = data_source.columns.all()
        serializer = DataColumnSerializer(columns, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def quality_report(self, request, pk=None):
        """
        Get quality report for a data source.
        """
        data_source = self.get_object()
        
        try:
            quality_report = data_source.quality_report
            serializer = DataQualityReportSerializer(quality_report)
            return Response(serializer.data)
        except DataQualityReport.DoesNotExist:
            return Response(
                {'error': 'Quality report not available. Run analysis first.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """
        Refresh data from source.
        """
        data_source = self.get_object()
        
        if data_source.source_type == 'file':
            return Response(
                {'error': 'File-based data sources cannot be refreshed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ingestion_service = DataIngestionService()
            result = ingestion_service.refresh_data_source(data_source)
            
            return Response({
                'message': 'Data source refreshed successfully',
                'result': result
            })
        
        except Exception as e:
            return Response(
                {'error': f'Refresh failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Allow unauthenticated for demo
def upload_file(request):
    """
    Upload and process a data file with AI analysis.
    """
    parser_classes = [MultiPartParser, FormParser]
    serializer = FileUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        with transaction.atomic():
            # Create data source
            file_data = serializer.validated_data

            # For demo purposes, handle user authentication
            from django.contrib.auth import get_user_model
            User = get_user_model()

            if request.user.is_authenticated:
                user = request.user
            else:
                # Create or get a demo user for testing
                user, created = User.objects.get_or_create(
                    username='demo_user',
                    defaults={
                        'email': 'demo@example.com',
                        'first_name': 'Demo',
                        'last_name': 'User'
                    }
                )

            data_source = DataSource.objects.create(
                user=user,
                name=file_data.get('name', file_data['file'].name),
                description=file_data.get('description', ''),
                source_type='file',
                file=file_data['file'],
                file_size=file_data['file'].size,
                file_type=file_data['file'].content_type,
                status='processing'
            )

            # Process file immediately for demo (not async)
            ingestion_service = DataIngestionService()
            result = ingestion_service.process_file_upload_with_ai(data_source.id)

            return Response(
                {
                    'message': 'File uploaded and analyzed successfully.',
                    'data_source': DataSourceSerializer(data_source).data,
                    'analysis': result
                },
                status=status.HTTP_201_CREATED
            )

    except Exception as e:
        return Response(
            {'error': f'Upload failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_database_connection(request):
    """
    Test database connection parameters.
    """
    serializer = DatabaseConnectionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        ingestion_service = DataIngestionService()
        result = ingestion_service.test_database_connection(
            serializer.validated_data
        )
        
        return Response({
            'success': True,
            'message': 'Database connection successful',
            'details': result
        })
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': f'Connection failed: {str(e)}'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_api_connection(request):
    """
    Test API connection parameters.
    """
    serializer = APIConnectionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        ingestion_service = DataIngestionService()
        result = ingestion_service.test_api_connection(
            serializer.validated_data
        )
        
        return Response({
            'success': True,
            'message': 'API connection successful',
            'details': result
        })
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': f'Connection failed: {str(e)}'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class DataTransformationViewSet(ModelViewSet):
    """
    ViewSet for managing data transformations.
    """
    serializer_class = DataTransformationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DataTransformation.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """
        Execute a data transformation.
        """
        transformation = self.get_object()
        
        try:
            ingestion_service = DataIngestionService()
            result = ingestion_service.execute_transformation(transformation)
            
            return Response({
                'message': 'Transformation executed successfully',
                'result': result
            })
        
        except Exception as e:
            return Response(
                {'error': f'Execution failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_supported_formats(request):
    """
    Get list of supported file formats and database types.
    """
    return Response({
        'file_formats': [
            {
                'extension': 'csv',
                'name': 'Comma Separated Values',
                'description': 'Text file with comma-separated values'
            },
            {
                'extension': 'xlsx',
                'name': 'Excel Workbook',
                'description': 'Microsoft Excel file format'
            },
            {
                'extension': 'xls',
                'name': 'Excel 97-2003',
                'description': 'Legacy Microsoft Excel format'
            },
            {
                'extension': 'json',
                'name': 'JSON',
                'description': 'JavaScript Object Notation'
            },
            {
                'extension': 'parquet',
                'name': 'Apache Parquet',
                'description': 'Columnar storage format'
            }
        ],
        'database_types': [
            {
                'type': 'postgresql',
                'name': 'PostgreSQL',
                'default_port': 5432
            },
            {
                'type': 'mysql',
                'name': 'MySQL',
                'default_port': 3306
            },
            {
                'type': 'sqlite',
                'name': 'SQLite',
                'default_port': None
            },
            {
                'type': 'oracle',
                'name': 'Oracle Database',
                'default_port': 1521
            },
            {
                'type': 'mssql',
                'name': 'Microsoft SQL Server',
                'default_port': 1433
            }
        ],
        'api_auth_types': [
            {
                'type': 'none',
                'name': 'No Authentication'
            },
            {
                'type': 'bearer',
                'name': 'Bearer Token'
            },
            {
                'type': 'basic',
                'name': 'Basic Authentication'
            },
            {
                'type': 'api_key',
                'name': 'API Key'
            }
        ]
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_stats(request):
    """
    Get user's data ingestion statistics.
    """
    user = request.user
    
    stats = {
        'total_data_sources': DataSource.objects.filter(user=user).count(),
        'active_data_sources': DataSource.objects.filter(
            user=user,
            status='completed'
        ).count(),
        'total_rows_processed': DataSource.objects.filter(
            user=user
        ).aggregate(
            total=models.Sum('rows_count')
        )['total'] or 0,
        'total_file_size_mb': DataSource.objects.filter(
            user=user
        ).aggregate(
            total=models.Sum('file_size')
        )['total'] or 0,
        'data_sources_by_type': DataSource.objects.filter(
            user=user
        ).values('source_type').annotate(
            count=models.Count('id')
        ),
        'recent_uploads': DataSource.objects.filter(
            user=user
        ).order_by('-created_at')[:5].values(
            'id', 'name', 'source_type', 'status', 'created_at'
        )
    }
    
    # Convert file size to MB
    if stats['total_file_size_mb']:
        stats['total_file_size_mb'] = round(
            stats['total_file_size_mb'] / (1024 * 1024), 2
        )
    
    return Response(stats)


class ETLOperationViewSet(ModelViewSet):
    """
    ViewSet for managing ETL operations.
    """
    serializer_class = ETLOperationSerializer
    permission_classes = [permissions.AllowAny]  # Temporarily allow unauthenticated access

    def get_queryset(self):
        # For now, return empty queryset since we don't have operations yet
        return ETLOperation.objects.none()

    def list(self, request):
        """
        List all ETL operations.
        """
        return Response({
            'results': [],
            'count': 0
        })

    def retrieve(self, request, pk=None):
        """
        Get a specific ETL operation.
        """
        return Response({
            'id': pk,
            'status': 'completed',
            'operation_type': 'data_ingestion',
            'progress': 100,
            'message': 'Operation completed successfully'
        })
