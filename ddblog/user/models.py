from django.db import models
import random


def default_sign():
    signs = ['健身达人', '码农', '队长', '马保国', '太极拳达人']
    return random.choice(signs)


# Create your models here.
class UserProfile(models.Model):
    username = models.CharField('姓名', max_length=11, primary_key=True)
    nickname = models.CharField('昵称', max_length=30)
    email = models.EmailField()
    password = models.CharField(max_length=32)
    sign = models.CharField('个人签名', max_length=50, default=default_sign)
    info = models.CharField('个人描述', max_length=150, default='')
    avatar = models.ImageField(upload_to='avatar', null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=11, default='')
