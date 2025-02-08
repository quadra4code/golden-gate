import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

# Create your utilities here.

class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = cls()
        token['user_id'] = user.id
        token['username'] = user.username
        token['roles'] = [gg.name for gg in user.groups.all()]
        return token

def generate_jwt_token(user):
    refresh = CustomRefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def extract_payload_from_jwt(token):
    try:
        payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError as e:
        return {'error': str(e), 'msg': 'Token is expired'}
    except jwt.InvalidTokenError as e:
        return {'error': str(e), 'msg': 'Invalid token'}
    except Exception as e:
        return {'error': str(e), 'msg': 'Unexpected error happened while decoding token'}
