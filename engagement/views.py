from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from engagement import services

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_notifications_view(request):
    result = services.all_notifications_service(request.user)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_read_view(request, notification_id):
    result = services.mark_read_service(request.user, notification_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_all_read_view(request):
    result = services.mark_all_read_service(request.user)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification_view(request, flag):
    result = services.delete_notification_service(request.user, flag)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)
