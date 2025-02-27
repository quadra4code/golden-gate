from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from admindash import services
from admindash import utils

# Create your views here.

@api_view(['POST'])
@permission_classes([utils.IsManagerUser, utils.IsAdminUser])
def paginated_staff_view(request):
    result = services.paginated_staff_service(request.data, request.headers)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['POST'])
@permission_classes([utils.IsManagerUser, utils.IsAdminUser])
def paginated_clients_view(request):
    result = services.paginated_clients_service(request.data)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

