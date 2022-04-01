from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
import html
import json
# Create your views here.

from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page

from tools.cache_dec import topic_cache
from tools.login_dec import login_check, get_user_by_request
from .models import Topic
from user.models import UserProfile

class TopicViews(View):

    def make_topic_res(self,author,author_topic,is_self):

        if is_self:
            next_topic=Topic.objects.filter(id__gt=author_topic.id,
                                            user_profile_id=author.username).first()
            last_topic=Topic.objects.filter(id__lt=author_topic.id,
                                            user_profile_id=author.username).last()
        else:
            next_topic = Topic.objects.filter(id__gt=author_topic.id,
                                              user_profile_id=author.username,
                                              limit='public').first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id,
                                              user_profile_id=author.username,
                                              limit='public').last()
        if next_topic:
            next_id=next_topic.id
            next_title=next_topic.title
        else:
            next_id = None
            next_title = None
        if last_topic:
            last_id = last_topic.id
            last_title = last_topic.title
        else:
            last_id = None
            last_title = None

        result={'code':200,'data':{}}
        result['data']['nickname']=author.nickname
        result['data']['title']=author_topic.title
        result['data']['category']=author_topic.category
        result['data']['content']=author_topic.content
        result['data']['introduce']=author_topic.introduce
        result['data']['author']=author.nickname
        result['data']['created_time']=author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        result['data']['last_id'] = last_id
        result['data']['last_title']=last_title
        result['data']['next_id']=next_id
        result['data']['next_title'] = next_title
        result['data']['messages'] = []
        result['data']['messages_count'] = 0
        return result


    def make_topics_res(self,author,author_topics):
        topics_res=[]
        for topic in author_topics:
            d={}
            d['id']=topic.id
            d['title']=topic.title
            d['category']=topic.category
            d['introduce']=topic.introduce
            d['created_time']=topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
            d['author']=author.nickname
            topics_res.append(d)
        res={'code':200,'data':{}}
        res['data']['topics']=topics_res
        res['data']['nickname']=author.nickname
        return res

    def clear_topic_caches(self,request):
        all_path=request.get_full_path()
        all_key_p=['topic_cache_self_','topic_cache_']
        all_key=[]
        for key_p in all_key_p:
            for key_h in ['','?category=tec','?category=no-tec']:
                all_key.append(key_p+all_path+key_h)
        print('--------all key-----')
        print(all_key)
        cache.delete_many(all_key)

    @method_decorator(login_check)
    def post(self,request,author_id):
        json_str=request.body
        json_obj=json.loads(json_str)
        content=json_obj['content']
        content_text=json_obj['content_text']
        introduce=content_text[:20]
        title=json_obj['title']
        title=html.escape(title)
        limit=json_obj['limit']
        if limit not in ['public','private']:
            result={'code':10300,'error':'the limit is error'}
            return JsonResponse(result)
        category=json_obj['category']
        if category not in ['tec','no-tec']:
            result={'code':10301,'error':'the category is error'}
            return JsonResponse(result)

        author=request.myuser
        Topic.objects.create(title=title,content=content,
                             limit=limit,category=category,
                             introduce=introduce,user_profile=author)

        self.clear_topic_caches(request)

        return JsonResponse({'code':200,'username':author.username})


    @method_decorator(topic_cache(600))
    def get(self,request,author_id):
        print('------get view in-----')
        try:
            author=UserProfile.objects.get(username=author_id)
        except Exception as e:
            result={'code':10305,'error':'the author id is error'}
            return JsonResponse(result)
        visitor_username=get_user_by_request(request)

        t_id=request.GET.get('t_id')
        is_self=False
        if t_id:
            if visitor_username==author_id:
                is_self=True
                try:
                    author_topic=Topic.objects.get(user_profile_id=author_id,
                                                                      id=t_id)

                except Exception as e:
                    result = {'code': 10310, 'error': 'the topic id is error'}
                    return JsonResponse(result)

            else:
                try:
                    author_topic =  Topic.objects.get(user_profile_id=author_id,
                                                                        id=t_id,limit='public')

                except Exception as e:
                    result = {'code': 10310, 'error': 'the topic id is error'}
                    return JsonResponse(result)

            res = self.make_topic_res(author, author_topic,is_self)
            return JsonResponse(res)

        else:

            category=request.GET.get('category')
            filter_category = False
            if category in ['tec','no-tec']:
                filter_category=True

            if author_id==visitor_username:
                if filter_category:
                    author_topics = Topic.objects.filter(user_profile_id=author_id,
                                                         category=category)
                else:
                    author_topics=Topic.objects.filter(user_profile_id=author_id)
            else:
                if filter_category:
                    author_topics = Topic.objects.filter(user_profile_id=author_id,
                                                         category=category,
                                                         limit='public')
                else:
                    author_topics = Topic.objects.filter(user_profile_id=author_id,
                                                    limit='public')

            res=self.make_topics_res(author,author_topics)
            return JsonResponse(res)