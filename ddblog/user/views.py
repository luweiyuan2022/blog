from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
import json
from user.models import UserProfile
import hashlib

import time
import jwt

from django.conf import settings
from tools.login_dec import login_check

import random
from tools.sms import YunTongXin
from .tasks import send_sms


class UsersView(View):
    def get(self, request,username=None):

        if username:
            try:
                user=UserProfile.objects.get(username=username)
            except Exception as e:
                print('-get user error is %s-' % e)
                result = {'code':10104,'error':'该用户不存在！'}
                return JsonResponse(result)

            keys=request.GET.keys()
            if keys:
                data={}
                for k in keys:
                    if k=='password':
                        continue
                    if hasattr(user,k):
                        data[k]=getattr(user,k)
                result={'code':200,'username':username,
                    'data':data}
            else:

                result={'code':200,'username':username,
                        'data':{
                            'info':user.info,'sign':user.sign,
                            'nickname':user.nickname,
                            'avatar':str(user.avatar)}}
            return JsonResponse(result)
        else:
            pass

        return HttpResponse('--users get---')

    def post(self, request):
        json_str=request.body
        json_obj=json.loads(json_str)
        username=json_obj['username']
        email=json_obj['email']
        phone=json_obj['phone']
        sms_num=json_obj['sms_num']
        cache_key='sms_%s' % phone
        old_code=cache.get(cache_key)
        # if not old_code:
        #     result = {'code': 10105, 'error': '验证码不正确！'}
        #     return JsonResponse(result)
        # if int(sms_num)!=old_code:
        #     result={'code':10104,'error':'验证码不正确！'}
        #     return JsonResponse(result)
        sms_num_2=str(cache.get('sms_%s' % phone))
        password_1=json_obj['password_1']
        password_2=json_obj['password_2']
        print(username,email,phone,password_1,password_2)
        if len(username)>11:
            result={'code':10100,'error':'用户名太长！'}
            return JsonResponse(result)
        old_user=UserProfile.objects.filter(username=username)
        if old_user:
            result={'code':10101,'error':'用户名已被占用！'}
            return JsonResponse(result)
        if password_1!=password_2:
            result={'code':10102,'error':'两次密码不一致！'}
            return JsonResponse(result)

        md5=hashlib.md5()
        md5.update(password_1.encode())
        password_h=md5.hexdigest()
        try:
            user=UserProfile.objects.create(username=username,
                                            password=password_h,
                                            email=email,
                                            phone=phone,
                                            nickname=username)
        except Exception as e:
            print('create error is %s' % e)
            result={'code':10103,'error':'用户名被占用！'}
            return JsonResponse(result)
        token=make_token(username)
        token=token.decode()
        return JsonResponse({'code': 200,'username':username,
                             'data':{'token':token}})

    @method_decorator(login_check)
    def put(self,request,username):
        json_str=request.body
        json_obj=json.loads(json_str)
        user=request.myuser
        user.sign=json_obj['sign']
        user.nickname=json_obj['nickname']
        user.info=json_obj['info']
        user.save()
        result = {'code':200, 'username': user.username}
        return JsonResponse(result)


def make_token(username,expire=3600*24):
    key=settings.JWT_TOKEN_KEY
    now=time.time()
    payload={'username':username,'exp':now+expire}
    return jwt.encode(payload,key,algorithm='HS256')

@login_check
def user_avatar(request,username):
    if request.method!='POST':
        result={'code':10105,'error':'必须是post请求！'}
        return JsonResponse(result)

    user=request.myuser
    user.avatar=request.FILES['avatar']
    user.save()
    result={'code':200,'username':username}
    return JsonResponse(result)

def sms_view(request):
    json_str=request.body
    json_obj=json.loads(json_str)
    phone=json_obj['phone']
    # print(phone)
    cache_key='sms_%s' % phone

    code=random.randint(1000,9999)
    cache.set(cache_key,code,65)
    print('--send code %s--'%code)
    # x=YunTongXin(settings.SMS_ACCOUNT_ID,
    # settings.SMS_ACCOUNT_TOKEN,
    # settings.SMS_APP_ID,
    # settings.SMx=YunTongXin(settings.SMS_ACCOUNT_ID,

    # res=x.run(phone,code)
    # res=send_sms.delay(phone,code)

    res=send_sms.delay(phone,code)
    print('--send sms result is %s--' % res)
    return JsonResponse({'code':200})




