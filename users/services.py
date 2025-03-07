from django.http import QueryDict
from users.models import CustomUser, UserPhoneNumber
from django.contrib.auth.models import Group
from core.base_models import ResultView
from users.serializers import ChangePasswordSerializer, LoginSerializer, RegisterSerializer, AccountViewSerializer, UpdateAccountSerializer
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
                    result.msg = 'خطأ فى بيانات الحساب'
                elif not user_to_auth.is_active:
                    result.msg = 'الحساب غير مفعل؛ برجاء التواصل مع الدعم'
                else:
                    logger.info(f"User {user_to_auth.username} logged in successfully.")
                    token_obj = generate_jwt_token(user_to_auth)
                    result.msg = 'تم تسجيل الدخول بنجاح'
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
                result.msg = 'حدث خطأ أثناء معالجة البيانات'
                result.data = {'errors': serialized_login_data.errors, 'error messages': serialized_login_data.error_messages}
    except Exception as e:
        result.msg = f'حدث خطأ أثناء تسجيل الدخول للمستخدم {username}.'
        result.data = {'error': str(e)}
    finally:
        return result

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
                'كلمة السر القديمة مطلوبة' if token and new_password and confirm_new_password
                else 'كلمة السر الجديدة مطلوبة' if token and confirm_new_password
                else 'تأكيد كلمة السر الجديدة مطلوب' if token
                else 'مستخدم غير مسموح به' if new_password and confirm_new_password and old_password
                else 'بيانات غير صحيحة'
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
                        result.msg = "كلمة السر القديمة خاطئة"
                    else:
                        if user_to_change_password:
                            user_to_change_password.set_password(new_password)
                            user_to_change_password.save()
                            result.data = {
                                'id': token_decode_result.get('user_id'),
                                'username': token_decode_result.get('username'),
                                'roles': token_decode_result.get('roles')
                            }
                            result.msg = 'تم تغيير كلمة السر بنجاح'
                            result.is_success = True
                        else:
                            result.msg = 'مستخدم غير مسموح به'
            else:
                result.msg = 'حدث خطأ أثناء معالجة البيانات'
                result.data = {'errors': serialized_change_password_data.errors, 'error messages': serialized_change_password_data.error_messages}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تغيير كلمة السر'
        result.data = {'error': str(e)}
    finally:
        return result

def account_service(user_obj):
    result = ResultView()
    try:
        if not user_obj:
            result.msg = 'هذا المستخدم غير موجود'
        else:
            serialized_user_data = AccountViewSerializer(user_obj)
            result.data = serialized_user_data.data
            result.msg = 'تم جلب بيانات الحساب بنجاح'
            result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب بيانات الحساب'
        result.data = {'errors': str(e)}
    finally:
        return result

def update_account_service(request_data, user_obj):
    result = ResultView()
    try:
        if not user_obj:
            result.msg = 'هذا المستخدم غير موجود'
        else:
            if isinstance(request_data, QueryDict):
                request_data = request_data.copy()
            serialized_user_to_update = UpdateAccountSerializer(user_obj, data=request_data, partial=True)
            if serialized_user_to_update.is_valid():
                serialized_user_to_update.save()
                result.data = serialized_user_to_update.data
                result.msg = 'تم تحديث الحساب بنجاح'
                result.is_success = True
            else:
                result.msg = 'حدث خطأ أثناء معالجة بيانات الحساب'
                result.data = serialized_user_to_update.errors
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تحديث الحساب'
        result.data = {'errors': str(e)}
    finally:
        return result

def leaderboard_service():
    result = ResultView()
    try:
        top_10_users = CustomUser.objects.order_by('-referral_count', 'first_name', 'last_name')[:10]
        result.data = [
            {'rank': idx+1, 'name': user.get_full_name(), 'referral_count': user.referral_count} 
            for idx, user in enumerate(top_10_users)
        ]
        result.is_success = True
        result.msg = 'تم جلب قائمة المتصدرين بنجاح'
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب قائمة المتصدرين'
        result.data = {'error': str(e)}
    finally:
        return result

