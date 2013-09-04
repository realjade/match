# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, session, url_for, redirect, \
        render_template, abort, g, flash, json, Response, make_response, current_app
import models as m
from models.tables import User,Admin,Classgrade,Task,Video,Works,School,TeacherFavor,\
        Taskbox,ClassTask,UserClass,TimeLine,TimeLineEvent
from lib.wrappers import login_required, parent_required, teacher_required
import lib.functions as f
import lib.datawrappers as dw
import lib.utils as ut
from lib import const
import time
from lib.filters import format_datetime
        
# Flask 模块对象
module = Blueprint('school', __name__)


@module.route('/api/class/getclassbyid/',methods=['GET','POST'])
@login_required
def get_classbyid():
    class_id = request.values.get('class_id','')
    classgrade = m.session.query(Classgrade).\
    filter(Classgrade.class_id == class_id).first()
    if not classgrade:
        return f.failed(*const.CLASSGRADE_NOT_EXIST)
    else:
        return f.succeed({'class_id':classgrade.class_id,
                    'classup':False,
                    'class_name':classgrade.class_name,
                    'tname':classgrade.creator.get("nickname",""),
                    'created':format_datetime(classgrade.created),
                    'school':classgrade.school,
                    "email":classgrade.email,
                    'studentcount':classgrade.studentcount,
                    'teachercount':classgrade.teachercount,
                    'description':classgrade.extra.get('description',''),
                    'alreadyin':False
                      })


@module.route('/api/class/join/',methods=['GET','POST'])
@login_required
def join_class():
    user = g.user
    if user.isparent:# 如果是家长
        user = user.child
    
    class_id = request.values.get('class_id','')
    course = request.values.get('course')
    classgrade = m.session.query(Classgrade).filter(Classgrade.class_id == class_id).first()
    if not classgrade:
        return f.failed(*const.CLASSGRADE_NOT_EXIST)
    user_id = user.user_id
    userclass = m.session.query(UserClass).filter(UserClass.class_id == class_id,
                                      UserClass.user_id == user_id,UserClass.valid == True).first()
    if userclass:
        return f.succeed(dw.wrap_classgrade(classgrade))
    else:
        userclass = UserClass(user_id=user_id, class_id = classgrade.class_id, is_creator = 0, 
            created = int(time.time()*1000), updated = int(time.time()*1000))
        if user.is_teacher:
            userclass.identity = 1
            userclass.course = course
        else:
            userclass.identity = 0
        m.session.add(userclass)

        if user.isstudent:
            classgrade.init_taskbox(user)
        if user.isparent:
            classgrade.init_taskbox(child)
        # first task
        firstjoin = request.values.get('firstjoin',False)
        if firstjoin:
            taskbox = Taskbox(task_id = u"4000000000000", user_id = user_id, 
                            class_id = classgrade.class_id,confirm = 0,
                            created = int(time.time()*1000), 
                            updated = int(time.time()*1000))
            m.session.add(taskbox)
        m.session.commit()
        return f.succeed(dw.wrap_classgrade(classgrade))
    
@module.route('/api/class/create/',methods=['GET','POST'])
@teacher_required
def create_class():
    school = request.values.get('school','')
    class_name = request.values.get('class_name','')
    class_description = request.values.get('class_description','')
    email = request.values.get('email','')# 公共邮箱
    result = {}
    result.update(isexist=False)
    # 创建班级
    class_id = ut.create_class_id()
    classgrade = Classgrade()
    classgrade.school = school
    classgrade.class_id = class_id
    classgrade.class_name = class_name
    classgrade.email = email
    classgrade.created = int(time.time()*1000)
    classgrade.updated = int(time.time()*1000)
    classgrade.extra['description'] = class_description
    m.session.add(classgrade)
    # 加入用户和班级的关联
    userclass = UserClass()
    userclass.user_id = g.user.user_id
    userclass.class_id = classgrade.class_id
    userclass.identity = 1
    userclass.course = g.user.course
    userclass.valid = 1
    userclass.is_creator = 1
    userclass.created = int(time.time()*1000)
    userclass.updated = int(time.time()*1000)
    m.session.add(userclass)
    m.session.commit()
    
    result.update(dw.wrap_classgrade(classgrade))
    return f.succeed(result)


@module.route('/api/class/update/',methods=['POST'])
@teacher_required
def udpate_class():
    """修改班级简介"""
    class_id = request.values.get('class_id','')
    class_desc = request.values.get('class_desc','')
    classgrade = m.session.query(Classgrade).filter(Classgrade.class_id == class_id).first()
    if not classgrade:
        return f.failed(*const.ClASS_NOT_EXIST)
        
    classgrade.extra['description'] = class_desc
    m.session.commit()
    return f.succeed({})


@module.route('/api/class/update/email/',methods=['POST'])
@teacher_required
def update_class_email():
    """修改公共邮箱"""
    class_id = request.values.get('class_id','')
    email = request.values.get('email','')
    classgrade = m.session.query(Classgrade).filter(Classgrade.class_id == class_id).first()
    if not classgrade:
        return f.failed(*const.ClASS_NOT_EXIST)
        
    classgrade.email = email
    m.session.commit()
    return f.succeed({})


@module.route('/api/class/update/school/',methods=['POST'])
@teacher_required
def update_class_school():
    """修改school"""
    class_id = request.values.get('class_id','')
    school = request.values.get('school','')
    classgrade = m.session.query(Classgrade).filter(Classgrade.class_id == class_id).first()
    if not classgrade:
        return f.failed(*const.ClASS_NOT_EXIST)
        
    classgrade.school = school
    m.session.commit()
    return f.succeed({})



