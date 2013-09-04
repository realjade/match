# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, session, url_for, redirect, render_template, g, flash, current_app, abort
import models as m
from werkzeug.datastructures import Headers
from models.tables import User,Classgrade, School,MobileCode
from lib.wrappers import login_required, parent_required, teacher_required, student_required, jsonify
from lib import const,sms
from werkzeug import check_password_hash, generate_password_hash
import time
import lib.utils as ut
import lib.functions as f
import os
import random
import string

module = Blueprint('register', __name__)

@module.route('/api/register/mobilecode/')# , methods=['POST']
@jsonify
def api_mobilecode():
    """老师注册 发送手机验证码"""
    abort(404)
    mobile = request.form.get('mobile','')
    if not ut.is_mobile(mobile):
        return const.INVALID_MOBILE
    elif User.get_user(mobile):
        return const.ACCOUNT_MOBILE_EXIST
    code = u''.join([random.choice(string.digits + string.lowercase) for i in range(0, 6)])
    mobilecode = m.session.query(MobileCode).filter(MobileCode.mobile == mobile).first()
    if mobilecode:
        mobilecode.code = code
        mobilecode.created = int(time.time()*1000)
    else:
        mobilecode = MobileCode()
        mobilecode.mobile = mobile
        mobilecode.code = code
        mobilecode.created = int(time.time()*1000)
        m.session.add(mobilecode)
    success = sms.send_valimobilecode(mobile, code)
    if success:
        m.session.commit()
        return 'ok'
    else:
        m.session.rollback()
        return const.INVALID_MOBILE_SEND


@module.route('/api/register/', methods=['POST'])#TODO 重构
@jsonify
def api_register():
    role = request.form.get('role',None)
    if not role or role not in ('teacher','student'):
        return const.INVALID_PARAMS
    email = request.form.get('email','')
    mobile = request.form.get('mobile','')
    password = request.form.get('password','')
    password2 = request.form.get('password2','')
    course = request.form.get('course',None)
    if not ut.is_email(email) and not ut.is_mobile(mobile):
        return const.INVALID_PARAMS
    elif User.get_user(email):
        return const.ACCOUNT_EMAIL_EXIST
    elif User.get_user(mobile):
        return const.ACCOUNT_MOBILE_EXIST
    elif not password:
        return const.INVALID_PARAMS
    elif password != password2:
        return const.INVALID_PARAMS
    else:
        #老师注册
        if role == 'teacher':
            nickname = request.form.get('nickname',None)
            #mobilecode = request.form.get('mobilecode',None)# 注释掉老师注册的手机验证码
            #mobilecode = m.session.query(MobileCode).filter(MobileCode.mobile == mobile).first()
            #if mobilecode:
            #    if not mobilecode.vali(mobilecode.code):
            #        return const.INVALID_MOBILE_CODE
            #else:
            #    return const.INVALID_PARAMS
            
            if not nickname or not course:
                return const.INVALID_PARAMS
            user = User(user_id = ut.create_user_id(),
                nickname=nickname, email=email,mobile=mobile,
                pw_hash=generate_password_hash(password),
                is_teacher= 1, is_student=0,is_parent=0,
                created=int(time.time()*1000), updated=int(time.time()*1000))
            user.extra.update({'course':course})
            user.extra.update(guide_step = 1)
            flash(u'欢迎 '+user.nickname+u' 加入背书吧')
            m.session.add(user)
            m.session.commit()
            session['user_id'] = user.user_id
        elif role == 'student':# 学生注册
            pname = request.form.get('pname',None)
            sname = request.form.get('sname',None)
            if not pname or not sname:
                return const.INVALID_PARAMS
            puser = User(user_id = ut.create_user_id(),
                nickname=pname, email='',mobile=mobile,
                pw_hash=generate_password_hash(password),
                is_teacher= 0, is_student=0,is_parent=1,
                created=int(time.time()*1000), updated=int(time.time()*1000))
            suser = User(user_id = ut.create_user_id(),
                nickname=sname, email=email,mobile='',
                pw_hash=generate_password_hash(password),
                is_teacher= 0, is_student=1,is_parent=0,
                created=int(time.time()*1000), updated=int(time.time()*1000))
            puser.extra.update(guide_step = 1)
            suser.extra.update(guide_step = 1)
            m.session.add(puser)
            m.session.add(suser)
            m.session.commit()
            f.add_student_account(puser,suser)
            session['user_id'] = puser.user_id
        return 'ok'


@module.route('/register/teacher/',defaults={'template':'register-teacher.html'})
@module.route('/register/parent_student/',defaults={'template':'register-student.html'})
def register(template,www=None):
    """注册老师或者家长"""
    if g.user:
        return redirect(url_for('home.home'))
    else:
        return render_template('register/%s' % (template,))


@module.route('/guide/')
@login_required
def guide_main():
    """用户处理未注册完成的跳转"""
    step = g.user.extra.get('guide_step',None)
    if (g.user.isparent or g.user.isstudent) and step:
        return redirect('/guide/ps/%d/'%(step))
    elif g.user.isteacher and step:
        return redirect('/guide/teacher/%d/'%(step))
    else:
        return redirect(url_for('home.home'))




@module.route('/guide/ps/<int:step>/', methods=['GET', 'POST'])
@login_required
def guide_ps(step):
    """家长和子女注册流程"""
    if not g.user.isparent and not g.user.isstudent:
        return redirect('/home/')
    if g.user.isparent:
        parent = g.user
        child = g.user.children[0]
    else:
        parent = g.user.parent
        child = g.user
    templates_map = {
        1 : 'guide/guide_ps_step1.html',
        2 : 'guide/guide_ps_step2.html',
        3 : 'guide/guide_ps_step3.html'
    }
    if request.method == 'POST':
        if step < 4:
            parent.extra.update(guide_step = step+1)
            child.extra.update(guide_step = step+1)
            m.session.commit()
            return redirect('/guide/ps/%d/'%(step+1))
    if step in templates_map:
        classgrade = None
        if step == 3:
            parent.extra.pop('guide_step')
            child.extra.pop('guide_step')
            m.session.commit()
            
            class_li = g.user.new_classgrades
            if class_li:
                classid = class_li[0]
                classgrade = m.session.query(Classgrade).filter(Classgrade.class_id==classid).first()
        return render_template(templates_map[step],classgrade=classgrade)
    else:
        parent.extra.pop('guide_step')
        child.extra.pop('guide_step')
        m.session.commit()
        return redirect('/home/')



@module.route('/guide/teacher/<int:step>/', methods=['GET', 'POST'])
@teacher_required
def guide_teacher(step):
    """老师注册流程"""
    guide_step = g.user.extra.get('guide_step',None)
    if step == guide_step == 1:
        return render_template('register/teacher/step1.html')
    elif step == 2:
        if guide_step == 1:
            g.user.extra.pop('guide_step')
            m.session.commit()
            return render_template('register/teacher/step3.html')
        else:
            return redirect('/register/ok/')
    
    return redirect('/guide/teacher/%d/'%(guide_step or 2),)


@module.route('/register/info/download/')
@login_required
def register_info_download():
    """下载注册信息"""
    if g.user.isteacher:
        teacher = g.user
        data = u"""教师姓名:%s
            \r\n教师邮箱:%s
            \r\n教师手机:%s
            \r\n邮箱和手机均可作为登录账户
            \r\n教师账户的密码为您注册时设置的密码。
            \r\n如果忘记密码？http://www.beishu8.com/forget/
            \r\n请使用邮箱或者手机找回""" % (teacher.nickname,teacher.email,teacher.mobile,)
    else:
        if g.user.isparent:
            parent = g.user
            children = g.user.children
        elif g.user.isstudent:
            parent = g.user.parent
            children = [g.user]
        else:
            abort(404)
        
        childdata = u""
        for child in children:
            childdata += u"学生姓名:%s\r\n学生登录帐号:%s\r\n\r\n" % (child.nickname,child.email)
        
        data = u"""家长姓名:%s
                    \r\n家长登录帐号:%s
                    \r\n\r\n%s
                    \r\n家长账户与学生账户的密码均为您注册时设置的密码。
                    \r\n如果忘记密码？http://www.beishu8.com/forget/
                    \r\n家长账户请使用手机号找回
                    \r\n学生账户用邮箱找回""" % (parent.nickname,parent.mobile,childdata,)
    filename = u"背书吧注册信息.txt"
    headers = Headers()
    headers.add('Content-Disposition', 'attachment',
                    filename=filename.encode("gb2312"))
    headers['X-Sendfile'] = 'filename'
    headers['Content-Length'] = len(data)
    mimetype = 'application/octet-stream'
    rv = current_app.response_class(data, mimetype=mimetype, headers=headers,
                                    direct_passthrough=True)
    return rv


@module.route('/register/ok/')
@login_required
def register_ok():
    """注册成功"""
    if g.user.isparent:
        return redirect('/child/%s/' % g.user.children[0])
    else:
        return redirect('/task/')

