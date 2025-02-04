from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.services import change_password_service, register_user_service, login_user_service

# Create your views here.

'''
0 : superuser
1 : manager
3 : admin
4 : sales
5 : buyer
6 : seller
7 : broker
input
{
    "first_name": "John",
    "last_name": "han",
    "phone_number": "01555807172",
    "email": "john@gmail.com",
    "user_type": "5",
    "password": "securepassword",
    "confirm_password": "securepassword"
}
output
{
    "is_success": true,
    "data": {
        "user_id": 8,
        "first_name": "John",
        "last_name": "han",
        "username": "01555807172",
        "email": "john@gmail.com",
        "role": "Client"
    },
    "msg": "User John created successfully"
}
'''
@api_view(["POST"])
def register_user_view(request):
    registeration_result = register_user_service(request.data)
    status_code = (
        status.HTTP_201_CREATED if registeration_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(registeration_result.to_dict(), status=status_code)

'''
input
{
    "username": "01555807172",
    "password": "securepassword"
}
output
{
    "is_success": true,
    "data": {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczODE5MDM0NSwiaWF0IjoxNzM3NTg1NTQ1LCJqdGkiOiIyZDE1OGI0OTFmN2U0NjgzYmVmMDI2ZDg4NWE3NDU0NCIsInVzZXJfaWQiOjgsInVzZXJuYW1lIjoiMDE1NTU4MDcxNzIiLCJyb2xlcyI6WyJDbGllbnQiXX0.LubLydnR7dYrzWL2UHBRCLYgGpxYCFmt4v1W3tSTlEk",
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM3ODQ0NzQ1LCJpYXQiOjE3Mzc1ODU1NDUsImp0aSI6ImRjOGU0NmM3Mzk4MDRhZjY5NzlmYTk4NzMyNjRkMDU2IiwidXNlcl9pZCI6OCwidXNlcm5hbWUiOiIwMTU1NTgwNzE3MiIsInJvbGVzIjpbIkNsaWVudCJdfQ.hcB0PR1smhR5KmON3eSSrzZpvNxh97riSK6prRtDa8A",
        "user": {
            "id": 8,
            "username": "01555807172",
            "full_name": "John"
        }
    },
    "msg": "Login Successful"
}
'''
@api_view(["POST"])
def login_user_view(request):
    login_result = login_user_service(request.data)
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
'''
input
{
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiIwMTU1NTgwNzE3MiIsImZ1bGxfbmFtZSI6IkpvaG4gaGFuIiwiZXhwIjoxNzM2OTM4OTM0LCJpYXQiOjE3MzY5Mzg3NTQsImlzcyI6ImdlbmVyYWxfZWNvbW1lcmNlX2JhY2tlbmQifQ.g4VSe9FfDMrfDycMX2y5YZMNTUuzNIT_IErP-OYlR2E",
    "old_password": "securepassword",
    "new_password": "123",
    "confirm_new_password": "123"
}
output
{
    "is_success": true,
    "data": {
        "id": 8,
        "username": "01555807172",
        "roles": [
            "Client"
        ]
    },
    "msg": "Changed password for user 01555807172 successfully"
}
'''

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    change_password_result = change_password_service(request)
    status_code = (
        status.HTTP_202_ACCEPTED if change_password_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(change_password_result.to_dict(), status=status_code)