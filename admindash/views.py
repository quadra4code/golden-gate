from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
# from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from admindash import services
from admindash import utils

# Create your views here.

@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def paginated_staff_view(request):
    result = services.paginated_staff_service(request.data)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def staff_roles_view(request):
    result = services.staff_roles_service()
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def add_staff_view(request):
    result = services.add_staff_service(request.data)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_active_user_view(request, user_id):
    result = services.toggle_active_user_service(user_id)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([utils.IsManagerOrAdminUser])
def delete_staff_view(request, staff_id):
    result = services.delete_staff_service(staff_id)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def paginated_clients_view(request):
    result = services.paginated_clients_service(request.data)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def paginated_unit_requests_view(request):
    result = services.paginated_unit_requests_service(request.data)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def paginated_contact_msgs_view(request):
    result = services.paginated_contact_msgs_service(request.data)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def solve_contact_msg_view(request, msg_id):
    result = services.solve_contact_msg_service(msg_id, request.user.id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)



