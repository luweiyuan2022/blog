import datetime
import hashlib
import base64
import json

import requests

class YunTongXin():
    base_url='https://app.cloopen.com:8883'

    def __init__(self,accountSid,accountToken,appId,templateId):
        self.accountSid=accountSid
        self.accountToken=accountToken
        self.appId=appId
        self.templateId=templateId

    def get_request_url(self,sig):
        self.url=self.base_url+'/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s'%(self.accountSid,sig)
        return self.url

    def get_timestamp(self):
        now=datetime.datetime.now()
        now_str=now.strftime("%Y%m%d%H%M%S")
        return now_str

    def get_sig(self,timestamp):
        s=self.accountSid+self.accountToken+timestamp
        md5=hashlib.md5()
        md5.update(s.encode())
        return md5.hexdigest().upper()

    def get_request_header(self,timestamp):
        s=self.accountSid+':'+timestamp
        b_s=base64.b64encode(s.encode()).decode()
        return {
            'Accept':'application/json',
            'Content-Type':'application/json;charset=utf-8',
            'Authorization':b_s,

        }

    def get_request_body(self,phone,code):
        data={
            'to':phone,
            'appId':self.appId,
            'templateId':self.templateId,
            'datas':[code,'3']
        }
        return data

    def do_request(self,url,header,body):
        res=requests.post(url=url,headers=header,data=json.dumps(body))
        return res.text

    def run(self,phone,code):
        timestamp=self.get_timestamp()
        sig=self.get_sig(timestamp)
        url=self.get_request_url(sig)
        # print(url)
        header=self.get_request_header(timestamp)
        # print(header)
        body=self.get_request_body(phone,code)
        # print(body)
        res=self.do_request(url,header,body)
        return res

if __name__=='__main__':

    aid="8aaf07087e7b9872017ebf3e2bef08dd"
    atoken="8d5eb9cab3454f64ab27e8d5fc5577a6"
    appid="8aaf07087e7b9872017ebf3e2d5f08e4"
    tid="1"

    x=YunTongXin(aid,atoken,appid,tid)
    res=x.run('15917841240','123456')
    print(res)