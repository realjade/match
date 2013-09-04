# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, render_template, g, current_app
import models as m
from werkzeug import check_password_hash, generate_password_hash
import time
from lib.wrappers import login_required
import lib.utils as ut
import lib.functions as f
import os
import random
import string
from lib import const
import Image
from models.tables import Notice, UserNotice, User
from flask.ext.sqlalchemy import Pagination
"""
    修改用户信息
"""

module = Blueprint('settings', __name__)


@module.route('/settings/', methods=['GET', 'POST'])
@module.route('/settings/profile/', methods=['GET', 'POST'])
@login_required
def setting_profile():
    error = None
    success = None
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        desc = request.form.get('desc')
        address = request.form.get('address')
        line_phone = request.form.get('line_phone')
        qq = request.form.get('qq')
        course = request.form.get('course',None)
        if nickname:
            g.user.nickname = nickname
        else:
            error = u'输入的昵称不能为空'
            return render_template('settings/settings_profile.html', error = error, success = success)
        
        if email and g.user.email != email:
            if User.get_user(email):
                error = u"邮箱已经被占用"
                return render_template('settings/settings_profile.html', error = error, success = success)
        g.user.email = email
        
        if mobile and g.user.mobile != mobile:
            if User.get_user(mobile):
                error = u"手机已经被占用"
                return render_template('settings/settings_profile.html', error = error, success = success)
        g.user.mobile = mobile
        
        if not ut.is_email(email) and not ut.is_mobile(mobile):
            error = u"邮箱或者手机格式不正确"
            return render_template('settings/settings_profile.html', error = error, success = success)
        
        if g.user.isteacher:
            g.user.extra.update(course = course)
        else:
            if g.user.course:
                g.user.extra.pop('course')
        
        profile = g.user.extra.get("profile",{})
        profile["desc"] = desc
        profile["address"] = address
        profile["line_phone"] = line_phone
        profile["qq"] = qq
        g.user.extra.update(profile=profile)
        m.session.commit()
        success = u'修改成功'
    return render_template('settings/settings_profile.html', error = error, success = success)


@module.route('/settings/password/', methods=['GET', 'POST'])
@login_required
def setting_password():
    error = None
    success = None
    if request.method == 'POST':
        oldpassword = request.form.get('oldpassword')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if not check_password_hash(g.user.pw_hash, oldpassword):
            error = u'密码不正确'
        elif password != password2 or len(password) < 6:
            error = u'两次输入的密码不一致'
        else:
            g.user.pw_hash = generate_password_hash(password);
            g.user.updated = int(time.time()*1000)
            m.session.commit()
            success = u'修改密码成功'
    return render_template('settings/settings_password.html', error = error, success = success)


@module.route('/settings/avatar/upload/', methods=['POST'])
@login_required
def settting_avatar_upload():
    """ajax上传头像"""
    file = request.files.get('file')
    if file and f.allowed_img_file(file.filename):
        ext = os.path.splitext(file.filename)[1]
        snapavatar,width,height = ut.user_img_save(file,'snapavatar%s' % ext)
        g.user.extra.update(snapavatar=snapavatar)
        m.session.commit()
        return f.succeed({'path':"%s?%s" % (snapavatar,u''.join([random.choice(string.digits + string.lowercase) for i in range(0, 6)])),
                          'width':width,
                          'height':height})
    return f.failed(*const.UPLOAD_FAIL)


@module.route('/settings/avatar/cut/',methods=["POST"])
@login_required
def setting_avatar_cut():
    """剪切图像"""
    x1 = int(request.form.get("x1"))
    y1 = int(request.form.get("y1"))
    width = int(request.form.get("width"))
    height = int(request.form.get("height"))
    
    snapavatar = g.user.extra.get("snapavatar",None)
    if snapavatar:
        # 获取绝对路径
        user_id = g.user.user_id
        path = os.path.join(current_app.root_path, snapavatar.replace("/","",1))
        # 打开图片
        img = Image.open(path)
        width = width if width < height else height
        img=img.transform((width,width),Image.EXTENT,(x1,y1,x1+width,y1+width))
        # 头像保存位置生成
        avatarfolder = 'static/avatars/%s/%s/%s'%(user_id[0:3], user_id[3:6], user_id[6:])
        savepath = os.path.join(current_app.root_path,avatarfolder)
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        for w in [150, 100, 50]:
            newimg = img.crop()
            newimg.thumbnail((w,w), Image.ANTIALIAS)
            newimg.save(os.path.join(savepath, '%d.jpg'%(w)), 'JPEG', quality=90)
        # 删除原图和信息
        os.remove(path)
        g.user.avatar = u"/%s" % avatarfolder
        g.user.extra.update(snapavatar="")
        m.session.commit()
        return f.succeed("ok")
    return f.failed(*const.UPLOAD_FAIL)

@module.route('/settings/avatar/', methods=['GET', 'POST'])
@login_required
def setting_avatar():
    """修改头像"""
    snapavatar = g.user.extra.get("snapavatar")
    if snapavatar:# 清除未剪切的头像
        g.user.extra.update(snapavatar="")
        m.session.commit()
        path = os.path.join(current_app.root_path, snapavatar.replace("/","",1))
        os.remove(path)
    return render_template('settings/settings-avatar.html')


@module.route("/settings/notice/")
@login_required
def setting_notice():
    """系统通知"""
    page = int(request.args.get("page","1"))# 当前页
    query = m.session.query(UserNotice, Notice)
    query = query.filter(UserNotice.accept_user == g.user.user_id)
    query = query.join(Notice, UserNotice.notice_id == Notice.notice_id)
    count = query.count()
    query = query.order_by(Notice.created.desc())
    noticelist = query.offset(page*10 - 10).limit(10).all()# 查询的具体数据
    pagination = Pagination(query,page,10,count,noticelist)# 每页10个
    return render_template('settings/settings_notice.html', pagination = pagination)


@module.route("/settings/notice/<notice_id>/read/")
@login_required
def setting_notice_read(notice_id):
    """确定通知已经读取"""
    query = m.session.query(UserNotice)
    query = query.filter(UserNotice.notice_id == notice_id)
    query = query.filter(UserNotice.accept_user == g.user.user_id)
    usernotice = query.first()
    if usernotice:
        usernotice.isread = 1
        m.session.commit()
        return f.succeed("ok")
    return f.failed("error")
