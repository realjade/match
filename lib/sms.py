# -*- coding: utf-8 -*-
import urllib, urllib2
from urllib2 import Request, urlopen
from werkzeug.urls import url_encode
from flask import json, g, session
import types
import random
import string
import time

suffix = u'[背书吧]'

def send_sms(to, message):
    if type(to) in types.StringTypes:
        to = [to]
    params = {'k':'5cd813aa68bc5be8a2f23c7de756d72a', 'p':'1', 'r':'json', 'c':message+suffix, 't':','.join(to)}
    encoded_params = url_encode(params)
    req = Request('http://tui3.com/api/send/?%s'%(encoded_params) )
    
    try:
        f = urlopen(req, timeout = 60)
        r = f.read()
        f.close()
        r = json.loads(r)
        if r['err_code'] == 0:
            return True
        else:
            return False
    except urllib2.URLError, e:
        return False
    except Exception,e:
        return False

def send_password(to,link):
    message = u'您的背书吧密码重置链接为:%s'%(link,)
    return send_sms(to, message)

def send_valimobilecode(to,code):
    """教师注册时 验证教师手机"""
    message = u"手机验证码：%s" % code
    return send_sms(to, message)

def verify_code(to, code):
    if 'smscode' in session:
        real_to = session['smscode'].get('to', '')
        real_code = session['smscode'].get('code', '')
        expired = session['smscode'].get('expired', '')
        if to == real_to and code == real_code and time.time() <= expired:
            session.pop('smscode')
            return True
    return False

if __name__ == '__main__':
    send_sms('13911513315', u'请填写您要接收上行短信的地址。管理员为您分配短信上行代码并审核通过后，才能使用。')
