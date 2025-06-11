"""
Views for AI Engine app.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .services import OpenRouterService
import logging
import time

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for AI Engine."""
    return Response({
        'status': 'healthy',
        'service': 'AI Engine',
        'version': '1.0.0'
    })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def conversations(request):
    """Handle AI conversations."""
    if request.method == 'GET':
        return Response({
            'conversations': [],
            'count': 0
        })
    elif request.method == 'POST':
        # Create a new conversation
        conversation_id = f"conv_{int(time.time())}"
        data_source_id = request.data.get('data_source_id')
        title = request.data.get('title', 'New Conversation')

        return Response({
            'id': conversation_id,
            'title': title,
            'data_source_id': data_source_id,
            'created_at': time.time(),
            'status': 'active'
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def test_ai_chat(request):
    """Test endpoint for OpenRouter AI chat functionality."""
    try:
        # Get message from request
        message = request.data.get('message', 'Hello, can you help me test the AI chat?')

        # Initialize OpenRouter service
        openrouter_service = OpenRouterService()

        # Prepare messages for chat completion
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant for an ETL (Extract, Transform, Load) platform. Be concise and helpful."
            },
            {
                "role": "user",
                "content": message
            }
        ]

        # Get AI response
        response = openrouter_service.chat_completion(messages)

        return Response({
            'status': 'success',
            'message': message,
            'ai_response': response['content'],
            'model': response['model'],
            'tokens_used': response['tokens_used'],
            'processing_time': response['processing_time']
        })

    except Exception as e:
        logger.error(f"AI chat test error: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def conversation_messages(request, conversation_id):
    """Handle messages in a conversation."""
    try:
        content = request.data.get('content', '')
        role = request.data.get('role', 'user')

        if not content:
            return Response({
                'status': 'error',
                'message': 'Message content is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # For now, just return a simple response
        # In a real implementation, you'd save this to a database
        message_id = f"msg_{int(time.time())}"

        # If it's a user message, generate an AI response
        if role == 'user':
            try:
                # Initialize OpenRouter service
                openrouter_service = OpenRouterService()

                # Prepare messages for chat completion
                messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant for an ETL (Extract, Transform, Load) platform. Be concise and helpful."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ]

                # Get AI response
                ai_response = openrouter_service.chat_completion(messages)

                return Response({
                    'status': 'success',
                    'user_message': {
                        'id': message_id,
                        'content': content,
                        'role': 'user',
                        'timestamp': time.time()
                    },
                    'ai_response': {
                        'id': f"msg_{int(time.time()) + 1}",
                        'content': ai_response['content'],
                        'role': 'assistant',
                        'timestamp': time.time(),
                        'model': ai_response['model'],
                        'tokens_used': ai_response['tokens_used']
                    }
                })

            except Exception as ai_error:
                logger.error(f"AI response error: {str(ai_error)}")
                return Response({
                    'status': 'success',
                    'user_message': {
                        'id': message_id,
                        'content': content,
                        'role': 'user',
                        'timestamp': time.time()
                    },
                    'ai_response': {
                        'id': f"msg_{int(time.time()) + 1}",
                        'content': "I apologize, but I'm having trouble processing your request right now. Please try again later.",
                        'role': 'assistant',
                        'timestamp': time.time(),
                        'error': str(ai_error)
                    }
                })
        else:
            # Just store the message
            return Response({
                'status': 'success',
                'message': {
                    'id': message_id,
                    'content': content,
                    'role': role,
                    'timestamp': time.time()
                }
            })

    except Exception as e:
        logger.error(f"Conversation message error: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
