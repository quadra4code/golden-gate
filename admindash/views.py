from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from admindash import services
from admindash import utils

# Create your views here.

# region Statistics
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

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def active_visitors_count_view(request):
    result = services.active_visitors_count_service()
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_403_FORBIDDEN if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)
# endregion

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

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def get_sales_staff_view(request):
    result = services.get_sales_staff_service()
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def reset_password_view(request, user_id):
    result = services.reset_password_service(user_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_400_BAD_REQUEST
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

@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def paginated_featured_units_view(request):
    result = services.paginated_featured_units_service(request.data)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def paginated_units_addition_requests_view(request):
    result = services.paginated_units_addition_requests_service(request.data)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def paginated_rejected_units_view(request):
    result = services.paginated_rejected_units_service(request.data)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def paginated_soft_deleted_units_view(request):
    result = services.paginated_soft_deleted_units_service(request.data)
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
def reset_unit_approval_view(request, unit_id):
    result = services.reset_unit_approval_service(unit_id, request.user.id)
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

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def approve_unit_addition_view(request, unit_id):
    result = services.approve_unit_addition_service(unit_id, request.user.id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def disapprove_unit_addition_view(request):
    result = services.disapprove_unit_addition_service(request.data, request.user.id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region Request
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminOrSalesUser])
def paginated_requests_view(request):
    result = services.paginated_requests_service(request.data, request.user)
    status_code = (
        status.HTTP_200_OK if result.is_success
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

@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def assign_sales_request_view(request):
    result = services.assign_sales_request_service(request.data, request.user)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
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

# region Consultation Type
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def create_consult_type_view(request):
    result = services.create_consult_type_service(request.data, request.user.id if request.user else None)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def read_consult_types_view(request):
    result = services.read_consult_types_service()
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PUT'])
@permission_classes([utils.IsManagerOrAdminUser])
def update_consult_type_view(request, consult_type_id):
    result = services.update_consult_type_service(request.data, request.user.id if request.user else None, consult_type_id)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([utils.IsManagerOrAdminUser])
def delete_consult_type_view(request, consult_type_id):
    result = services.delete_consult_type_service(consult_type_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_hidden_consult_type_view(request, consult_type_id):
    result = services.toggle_hidden_consult_type_service(consult_type_id, request.user if request.user else None)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region Consulation
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def create_consultation_view(request):
    result = services.create_consultation_service(request.data, request.user.id if request.user else None)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def read_consultations_view(request, consult_type_id):
    result = services.read_consultations_service(consult_type_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PUT'])
@permission_classes([utils.IsManagerOrAdminUser])
def update_consultation_view(request, consultation_id):
    result = services.update_consultation_service(request.data, request.user.id if request.user else None, consultation_id)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([utils.IsManagerOrAdminUser])
def delete_consultation_view(request, consultation_id):
    result = services.delete_consultation_service(consultation_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_hidden_consultation_view(request, consultation_id):
    result = services.toggle_hidden_consultation_service(consultation_id, request.user if request.user else None)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region Client Reviews
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def read_reviews_view(request):
    result = services.read_reviews_service(request.data)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_hidden_review_view(request, review_id):
    result = services.toggle_hidden_review_service(review_id, request.user.id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([utils.IsManagerOrAdminUser])
def delete_review_view(request, review_id):
    result = services.delete_review_service(review_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)
# endregion




# region Unit Type
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def create_unit_type_view(request):
    result = services.create_unit_type_service(request.data, request.user)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def read_unit_types_view(request):
    result = services.read_unit_types_service()
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PUT'])
@permission_classes([utils.IsManagerOrAdminUser])
def update_unit_type_view(request, unit_type_id):
    result = services.update_unit_type_service(request.data, request.user, unit_type_id)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([utils.IsManagerOrAdminUser])
def delete_unit_type_view(request, unit_type_id):
    result = services.delete_unit_type_service(unit_type_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_hidden_unit_type_view(request, unit_type_id):
    result = services.toggle_hidden_unit_type_service(unit_type_id, request.user)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    print(status_code)
    return Response(result.to_dict(), status=status_code)
# endregion

# region Proposal
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def create_proposal_view(request):
    result = services.create_proposal_service(request.data, request.user)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def read_proposals_view(request):
    result = services.read_proposals_service()
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PUT'])
@permission_classes([utils.IsManagerOrAdminUser])
def update_proposal_view(request, proposal_id):
    result = services.update_proposal_service(request.data, request.user, proposal_id)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([utils.IsManagerOrAdminUser])
def delete_proposal_view(request, proposal_id):
    result = services.delete_proposal_service(proposal_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_hidden_proposal_view(request, proposal_id):
    result = services.toggle_hidden_proposal_service(proposal_id, request.user)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region Project
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def create_project_view(request):
    result = services.create_project_service(request.data, request.user)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def read_projects_view(request):
    result = services.read_projects_service()
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PUT'])
@permission_classes([utils.IsManagerOrAdminUser])
def update_project_view(request, project_id):
    result = services.update_project_service(request.data, request.user, project_id)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([utils.IsManagerOrAdminUser])
def delete_project_view(request, project_id):
    result = services.delete_project_service(project_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_hidden_project_view(request, project_id):
    result = services.toggle_hidden_project_service(project_id, request.user)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region City
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def create_city_view(request):
    result = services.create_city_service(request.data, request.user)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def read_cities_view(request):
    result = services.read_cities_service()
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PUT'])
@permission_classes([utils.IsManagerOrAdminUser])
def update_city_view(request, city_id):
    result = services.update_city_service(request.data, request.user, city_id)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([utils.IsManagerOrAdminUser])
def delete_city_view(request, city_id):
    result = services.delete_city_service(city_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_hidden_city_view(request, city_id):
    result = services.toggle_hidden_city_service(city_id, request.user)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region Region
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def create_region_view(request):
    result = services.create_region_service(request.data, request.user)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def read_regions_view(request):
    result = services.read_regions_service()
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PUT'])
@permission_classes([utils.IsManagerOrAdminUser])
def update_region_view(request, region_id):
    result = services.update_region_service(request.data, request.user, region_id)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([utils.IsManagerOrAdminUser])
def delete_region_view(request, region_id):
    result = services.delete_region_service(region_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_hidden_region_view(request, region_id):
    result = services.toggle_hidden_region_service(region_id, request.user)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region Status
@api_view(['POST'])
@permission_classes([utils.IsManagerOrAdminUser])
def create_status_view(request):
    result = services.create_status_service(request.data, request.user)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([utils.IsManagerOrAdminUser])
def read_status_view(request):
    result = services.read_status_service()
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PUT'])
@permission_classes([utils.IsManagerOrAdminUser])
def update_status_view(request, status_id):
    result = services.update_status_service(request.data, request.user, status_id)
    status_code = (
        status.HTTP_201_CREATED if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([utils.IsManagerOrAdminUser])
def delete_status_view(request, status_id):
    result = services.delete_status_service(status_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PATCH'])
@permission_classes([utils.IsManagerOrAdminUser])
def toggle_hidden_status_view(request, status_id):
    result = services.toggle_hidden_status_service(status_id, request.user)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(result.to_dict(), status=status_code)
# endregion

