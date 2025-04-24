from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom exception handler to provide meaningful error messages.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Add custom error structure
        return Response({
            'error': True,
            'message': response.data,
            'status_code': response.status_code
        }, status=response.status_code)

    # Handle exceptions not caught by DRF's default handler
    return Response({
        'error': True,
        'message': 'An unexpected error occurred.',
        'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)