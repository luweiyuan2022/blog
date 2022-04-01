from django.http import JsonResponse
from django.shortcuts import render
import json
# Create your views here.
from django.views import View
from user.models import UserProfile
import hashlib
from user.views import make_token


class TokenView(View):
    def post(self,request):
        json_str=request.body
        json_body=json.loads(json_str)
        username=json_body['username']
        password=json_body['password']
        print(username,password)
        try:
            user=UserProfile.objects.get(username=username)
        except Exception as e:
            print('error is %s' % e)
            result={'code':10200,'error':'用户或密码错误！'}
            return JsonResponse(result)
        md5=hashlib.md5()
        md5.update(password.encode())
        if md5.hexdigest()!=user.password:
            result = {'code': 10200, 'error': '用户或密码错误！'}
            return JsonResponse(result)
        token=make_token(username)
        token=token.decode()
        result={'code': 200,'username':username,
                             'data':{'token':token}}
        return JsonResponse(result)