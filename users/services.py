from users.models import CustomUser, UserPhoneNumber
from django.contrib.auth.models import Group
from core.base_models import ResultView
from users.serializers import ChangePasswordSerializer, LoginSerializer, RegisterSerializer
from django.contrib.auth import authenticate
from users.utils import extract_payload_from_jwt, generate_jwt_token
import logging

# Create your services here.

def register_user_service(registration_data):
    result = ResultView()
    try:
        phone_as_username = registration_data.get("username", '')
        email = registration_data.get("email", '')
        password = registration_data.get("password", '')
        confirm_password = registration_data.get("confirm_password", '')
        if not password or password != confirm_password:
            result.msg = f"{'Passwords Don\'t match' if password else 'Password is required'}"
        elif UserPhoneNumber.objects.filter(phone_number=phone_as_username).exists() or CustomUser.objects.filter(username=phone_as_username, email=email).exists():
            result.msg = 'This user already exists, please login'
        else:
            serialized_new_user_data = RegisterSerializer(data=registration_data) # here we should set the is_active to false and turn it on when verified phone number
            if serialized_new_user_data.is_valid():
                new_user = serialized_new_user_data.save()
                UserPhoneNumber.objects.create(
                    phone_number=phone_as_username,
                    is_main_number=True,
                    created_by=new_user
                )
                # import requests
                # import environ
                # env = environ.Env()
                # environ.Env.read_env()
                # releans_api_key = env('RELEANS_API_KEY')
                # # send sms to verify the phone number
                # url = "https://api.releans.com/v2/otp/send"
                # payload = {
                #     'sender':'Golden Gate',#+447700900123
                #     'mobile':f'+2{phone_as_username}',
                #     'channel':'sms'}
                # headers = {
                # 'Authorization': f'Bearer {releans_api_key}'
                # }
                # response = requests.post(url, headers=headers, data = payload)
                # print(response.text)
            # verify code
            # url = "https://api.releans.com/v2/otp/check"
            # payload = {
            #     'mobile':'+201118069749',
            #     'code':'645823'}
            # headers = {
            # 'Authorization': f'Bearer {releans_api_key}'
            # }
            # response = requests.post(url, headers=headers, data = payload)
            # print(response.text)
                client_group, created = Group.objects.get_or_create(name='Client')
                new_user.groups.add(client_group)
                user_to_auth = authenticate(username=phone_as_username, password=password)
                token_obj = generate_jwt_token(user_to_auth)
                result.data = {
                    'refresh_token': token_obj.get('refresh'),
                    'access_token': token_obj.get('access'),
                    'user_id': new_user.id,
                    'first_name': new_user.first_name,
                    'last_name': new_user.last_name,
                    'username': new_user.username,
                    'email': new_user.email,
                    'role': new_user.groups.filter(name="Client").first().name,
                    'referral_code': new_user.referral_code
                }
                result.msg = f"User {new_user.first_name} created successfully"
                result.is_success = True
            else:
                result.msg = f'Error happened while serializing new user data'
                result.data = {'errors': serialized_new_user_data.errors, 'error messages': serialized_new_user_data.error_messages}
    except Exception as e:
        result.msg = f'Unexpected error happened while registering new user'
        result.data = {'error': str(e)}
    finally:
        return result


def login_user_service(login_data):
    result = ResultView()
    logger = logging.getLogger(__name__)
    try:
        username = login_data.get('username', '').strip()
        password = login_data.get('password', '').strip()
        if not username or not password:
            result.msg = 'Username is required' if password else 'Password is required' if username  else 'Username & Password are required'
        else:
            serialized_login_data = LoginSerializer(data=login_data)
            if serialized_login_data.is_valid():
                user_to_auth = authenticate(username=username, password=password)
                if user_to_auth is None:
                    logger.warning(f"Failed login attempt for username {username}.")
                    result.msg = 'Invalid Credentials'
                elif not user_to_auth.is_active:
                    result.msg = 'Account is not active. Please contact support'
                else:
                    logger.info(f"User {user_to_auth.username} logged in successfully.")
                    token_obj = generate_jwt_token(user_to_auth)
                    result.msg = 'Login Successful'
                    result.data = {
                        'refresh_token': token_obj.get('refresh'),
                        'access_token': token_obj.get('access'),
                        'user': {
                            'id': user_to_auth.id,
                            'username': user_to_auth.username,
                            'full_name': user_to_auth.first_name,
                            'referral_code': user_to_auth.referral_code,
                        }
                    }
                    result.is_success = True
            else:
                result.msg = f'Error happened while serializing login data'
                result.data = {'errors': serialized_login_data.errors, 'error messages': serialized_login_data.error_messages}
    except Exception as e:
        result.msg = f'Unexpected error happened while logging in user {username}.'
        result.data = {'error': str(e)}
    finally:
        return result


# def login_admin_service(username, password):
#     result = ResultView()
#     try:
#         print('in try')
#         if username and password:
#             print('there is username and password')
#             user = CustomUser.objects.get(username=username)
#             print('user found and it\'s', user, sep='=>')
#             if user.check_password(password):
#                 print('password is correct')
#                 result.data = user
#                 result.msg = f'User {user.username} logged in successfully'
#                 result.is_success = True
#             else:
#                 print('password is not correct')
#                 result.msg = 'Invalid Credentials'
#         else:
#             print('either username or password is missing')
#             result.msg = 'Username & Password are required' if not (username or password) else 'Username is required' if password else 'Password is required'
#     except Exception as e:
#         result.msg = f'Unexpected error happened while logging user {username} in.'
#         result.data = {'error': str(e)}
#     finally:
#         return result

def change_password_service(request):
    result = ResultView()
    try:
        token = request.headers.get('Authorization', '')
        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')
        confirm_new_password = request.data.get('confirm_new_password', '')
        if new_password != confirm_new_password:
            result.msg = 'Passwords Don\'t Match'
        elif not (token or old_password or new_password, confirm_new_password):
            result.msg = (
                'Old Password is required' if token and new_password and confirm_new_password
                else 'New Password is required' if token and confirm_new_password
                else 'Confirm New Password is required' if token
                else 'Unauthorized User' if new_password and confirm_new_password and old_password
                else 'Invalid Data'
            )
        else:
            serialized_change_password_data = ChangePasswordSerializer(data={
                'old_password': old_password,
                'new_password': new_password,
                'confirm_new_password': confirm_new_password
            })
            if serialized_change_password_data.is_valid():
                token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
                if token_decode_result.get('error'):
                    result.data = {'error': token_decode_result.get('error')}
                    result.msg = token_decode_result.get('msg')
                else:
                    user_to_change_password = CustomUser.objects.filter(id=token_decode_result.get('user_id')).first()
                    if not user_to_change_password.check_password(old_password):
                        result.msg = "Invalid old password"
                    else:
                        if user_to_change_password:
                            user_to_change_password.set_password(new_password)
                            user_to_change_password.save()
                            result.data = {
                                'id': token_decode_result.get('user_id'),
                                'username': token_decode_result.get('username'),
                                'roles': token_decode_result.get('roles')
                            }
                            result.msg = 'Password changed successfully'
                            result.is_success = True
                        else:
                            result.msg = 'Unauthorized User'
            else:
                result.msg = 'Error happen while serializing new password data'
    except Exception as e:
        result.msg = 'Unexpected error happened while changing password'
        result.data = {'error': str(e)}
    finally:
        return result