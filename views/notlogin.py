# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, redirect,render_template, abort
import models as m
from models.tables import User,Feedback, Passwordreset
from werkzeug import generate_password_hash
from sqlalchemy import desc
import time
import lib.functions as f
from lib import const,mail,sms
import string
from random import choice


module = Blueprint('notlogin', __name__)


@module.route('/aboutus/',defaults={"template":'notlogin/aboutus.html'})
@module.route('/help/',defaults={'template':'notlogin/help.html'})
@module.route('/license/',defaults={'template':'notlogin/license.html'})
@module.route('/vtime/',defaults={'template':'notlogin/vtime.html'})
def notlogin(template):
    return render_template(template)


@module.route('/feedback/', methods=['GET', 'POST'])
def feedback():
    error = None
    if request.method == 'POST':
        content = request.values.get('content','')
        name = request.values.get('name','')
        email = request.values.get('email','')
        feedback = Feedback(content = content,name=name,email=email,readed = False,
                            created = time.time()*1000,updated = time.time()*1000)
        m.session.add(feedback)
        m.session.commit()
    feedbacks = m.session.query(Feedback).order_by(desc(Feedback.created)).all()
    feedbacks = feedbacks[:20]
    return render_template('notlogin/feedback.html',error = error,feedbacks=feedbacks)


@module.route('/forget/',methods=['GET','POST'])
def reset():
    error = None
    if request.method == 'POST':
        email = request.values.get('email','')
        mobile = request.values.get('mobile','')
        if not email and not mobile:
            error = u'请输入邮箱或者手机号码'
        elif email:
            user = User.get_user(email)
            if not user:
                error = u'用户不存在'
            else:
                forget_code = ''.join([choice(string.digits) for i in range(0,10)])
                passwordreset = Passwordreset(user_id = user.user_id,code=forget_code,
                            created = time.time()*1000,)
                m.session.add(passwordreset)
                success = mail.smtp_send_mail([email], {'event':'forget','forget_code':forget_code,"user":user})
                if not success:
                    m.session.rollback()
                    error = u'密码重置失败'
                else:
                    m.session.commit()
                    return redirect('/forget/ok?email=%s'%(email))
        else:
            user = User.get_user(mobile)
            if not user:
                error = u'用户不存在'
            else:
                #change password and send it to user mobile
                forget_code = ''.join([choice(string.digits) for i in range(0,10)])
                link = "beishu8.com/pr/%s" % forget_code
                passwordreset = Passwordreset(user_id = user.user_id,code=forget_code,
                            created = time.time()*1000,)
                m.session.add(passwordreset)
                success = sms.send_password(mobile,link)
                if not success:
                    m.session.rollback()
                    error = u'密码重置失败'
                else:
                    m.session.commit()
                    return redirect('/forget/ok?mobile=%s'%(mobile))
    return render_template('notlogin/forget/forget.html',error = error)


@module.route('/forget/ok/')
def reset_ok():
    email = request.args.get('email')
    mobile = request.args.get('mobile')
    if not email and not mobile:
        return redirect('/')
    return render_template('notlogin/forget/forget-ok.html', email = email, mobile = mobile)


@module.route('/pr/<code>/',methods=['GET','POST'])
def forget_reset(code):
    """重置密码的修改页面"""
    pwdreset = m.session.query(Passwordreset).filter(Passwordreset.code == code).first()
    if not pwdreset or time.time() - pwdreset.created > 60*60*24:
        abort(404)
    user = m.session.query(User).filter(User.user_id == pwdreset.user_id).first()
    if not user:abort(404)
    error = None
    if request.method == 'POST':
        password = request.form.get('password','')
        password2 = request.form.get('password2','')
        if not password:
            error = const.INVALID_PASSWORD[1]
        elif password != password2:
            error = const.INVALID_TWICEPASS[1]
        else:
            user.pw_hash = generate_password_hash(password)
            m.session.query(Passwordreset).filter(Passwordreset.user_id == user.user_id).delete()
            m.session.commit()
            return redirect('/')
    
    return render_template('notlogin/forget/forget-reset.html',error = error)







