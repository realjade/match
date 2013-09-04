# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, redirect, render_template, g, abort
import models as m
from models.tables import User,Classgrade
from werkzeug import check_password_hash, generate_password_hash
import time
import lib.utils as ut
import lib.datawrappers as dw
from lib.wrappers import login_required, parent_required, teacher_required
import lib.functions as f


module = Blueprint('parent', __name__)


@module.route('/child/<child_id>/')
@parent_required
def child_info(child_id):
    child = m.session.query(User).filter(User.user_id == child_id).first()
    classgrades = child.classgrades_model()
    return render_template('parent/parent-mychildren.html',tab='child',child=child,subtab=child.user_id,classgrades=classgrades)


@module.route('/parent/addchild/', methods=['GET','POST'])
@parent_required
def parent_addchild():
    """父母为添加新的子女 创建帐号"""
    if request.method == "GET":
        return render_template('parent/parent-addchild.html')
    
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        pwd = request.form['pwd']
        cpwd = request.form['cpwd']
        
        if not name:
            error = u'请输入真实姓名'
        elif not ut.is_email(email):
            error = u'输入有效的邮箱'
        elif User.get_user(email) is not None:
            error = u'该邮箱已经存在'
        elif not pwd:
            error = u'密码不能为空'
        elif pwd != cpwd:
            error = u'两次密码不一致'
        else:
            user = User(user_id = ut.create_user_id(),
                    nickname=name, email=email,mobile='',
                    pw_hash=generate_password_hash(pwd),
                    is_teacher= 0, is_student=1,is_parent=0,
                    created=int(time.time()*1000), updated=int(time.time()*1000))
            m.session.add(user)
            m.session.commit()
            f.add_student_account(g.user,user)
            return f.succeed({'child_id':user.user_id})
        return f.failed(2,error)


@module.route('/parent/addchild/<child_id>/info/', methods=['GET'])
@parent_required
def parent_addchild_info(child_id):
    """父母为添加新的子女 显示帐号信息"""
    return render_template('parent/parent-addchild_info.html')


