from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from admindash import services
from admindash import utils

# Create your views here.

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def main_statistics_view(request):
    result = services.main_statistics_service()
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_403_FORBIDDEN if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

# region Staff | Users
@api_view(['POST'])
def staff_login_view(request):
    result = services.staff_login_service(request.data)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_403_FORBIDDEN if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

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

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def change_staff_permissions_view(request):
    result = services.change_staff_permissions_service(request.data)
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
# endregion

# region Units
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def paginated_units_view(request):
    result = services.paginated_units_service(request.data)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def unit_requests_user_view(request, unit_id):
    result = services.unit_requests_user_service(unit_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def update_unit_status_view(request, unit_id, status_id):
    result = services.update_unit_status_service(unit_id, status_id, request.user.id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_unit_deleted_view(request, unit_id):
    result = services.toggle_unit_deleted_service(unit_id, request.user.id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_unit_featured_view(request, unit_id):
    result = services.toggle_unit_featured_service(unit_id, request.user.id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region Request
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def paginated_requests_view(request):
    result = services.paginated_requests_service(request.data)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def change_request_status_view(request):
    result = services.change_request_status_service(request.data, request.user)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region Contact Us
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

@api_view(['DELETE'])
@permission_classes([utils.IsManagerOrAdminUser])
def delete_contact_msg_view(request, msg_id):
    result = services.delete_contact_msg_service(msg_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region Article
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def create_article_view(request):
    result = services.create_article_service(request.data, request.user.id if request.user else None)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def read_articles_view(request):
    result = services.read_articles_service()
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PUT'])
@permission_classes([utils.IsManagerOrAdminUser])
def update_article_view(request, article_id):
    result = services.update_article_service(request.data, request.user.id if request.user else None, article_id)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([utils.IsManagerOrAdminUser])
def delete_article_view(request, article_id):
    result = services.delete_article_service(article_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_hidden_article_view(request, article_id):
    result = services.toggle_hidden_article_service(article_id, request.user if request.user else None)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region Consultation

# endregion





