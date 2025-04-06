from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users import services

# Create your views here.

'''
0 : superuser
1 : manager
3 : admin
4 : sales
5 : buyer
6 : seller
7 : broker
'''
@api_view(["POST"])
def register_user_view(request):
    registeration_result = services.register_user_service(request.data)
    status_code = (
        status.HTTP_201_CREATED if registeration_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(registeration_result.to_dict(), status=status_code)

@api_view(["POST"])
def login_user_view(request):
    login_result = services.login_user_service(request.data)
    status_code = (
        status.HTTP_202_ACCEPTED if login_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(login_result.to_dict(), status=status_code)
    # import requests
    # url = "https://api.releans.com/v2/message"
    # payload = {
    #     "sender": "Golden Gate",
    #     "mobile": "+201118069749",
    #     "content": "Hello from Releans API"
    # }
    # headers = {
    # 'Authorization': 'Bearer your api key'
    # }
    # response = requests.request("POST", url, headers=headers, data = payload)
    # print(response.text.encode('utf8'))
    # return Response(data={"msg": response.text.encode('utf8')}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    change_password_result = services.change_password_service(request)
    status_code = (
        status.HTTP_202_ACCEPTED if change_password_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(change_password_result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_view(request):
    account_result = services.account_service(request.user if request.user else None)
    status_code = (
        status.HTTP_200_OK if account_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(account_result.to_dict(), status=status_code)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_account_view(request):
    update_account_result = services.update_account_service(request.data, request.user if request.user else None)
    status_code = (
        status.HTTP_200_OK if update_account_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(update_account_result.to_dict(), status=status_code)

@api_view(['GET'])
def leaderboard_view(request):
    leaderboard_result = services.leaderboard_service()
    status_code = (
        status.HTTP_200_OK if leaderboard_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(leaderboard_result.to_dict(), status=status_code)


