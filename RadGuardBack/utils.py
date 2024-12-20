# utils.py
from rest_framework_simplejwt.tokens import AccessToken
from myapi.models import User

def get_token_from_request(request):
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]  # 'Bearer' виступає як ключовий префікс, тому ми беремо наступний елемент
        return token
    return None

def get_user_from_token(token):
    try:
        token_obj = AccessToken(token)
        user_id = token_obj['user_id']
        user = User.objects.get(id=user_id)
        return user
    except Exception as e:
        return None
