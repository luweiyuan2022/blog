from django.http import JsonResponse
import jwt
from django.conf import settings
from user.models import UserProfile

def login_check(func):
    def wrap(request,*args,**kwargs):
        token=request.META.get('HTTP_AUTHORIZATION')
        if not token:
            result={'code':403,'error':'请登录'}
            return JsonResponse(request)
        try:
            payload=jwt.decode(token,settings.JWT_TOKEN_KEY,algorithm='HS256')
        except Exception as e:
            print('check login error %s' % e)
            result = {'code': 403, 'error': '请登录'}
            return JsonResponse(request)
        username=payload['username']
        user=UserProfile.objects.get(username=username)
        request.myuser=user
        return func(request,*args,**kwargs)
    return wrap

def get_user_by_request(request):
    token=request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None
    try:
        res=jwt.decode(token,settings.JWT_TOKEN_KEY)
    except Exception as e:
        print('get user jwt is error %s' % e)
        return None
    username=res['username']
    return username