# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, session, url_for, redirect, \
        render_template, abort, g, flash, json, Response, make_response, current_app,send_file
import models as m
from models.tables import User,Admin,Classgrade,Task,Video,Works,School,TeacherFavor,\
        Taskbox,ClassTask,UserClass,TimeLine,Feedback
from werkzeug import check_password_hash, generate_password_hash
from werkzeug import secure_filename
from sqlalchemy import or_,desc
import time
import pickle
import lib.utils as ut
from lib.wrappers import m_login_required
import lib.functions as f
import lib.filters as flt
from lib.videohelper import VideoHelper
from lib import const, videoworks
import os
import string
from random import choice
import types
from datetime import datetime, timedelta
import lib.datawrappers as dw
from flask.ext.sqlalchemy import Pagination

module = Blueprint('mobile', __name__)

@module.route('/m/', methods=['GET','POST'])
def m_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        remember = request.form.get('remember', None) == 'on'
        password = request.form['password']
        user = User.get_user(username)
        if user is None:
            error = u'邮箱或者手机号不正确'
        elif not user.check_password_hash(password):
            error = u'密码不正确'
        elif 'guide_step' in user.extra:
            error = u'改账户不可用，请到网站端处理'
        else:
            session['user_id'] = user.user_id
            if remember:
                session.permanent = True
            return redirect(url_for('mobile.m_home'))
    if g.user:
        if 'guide_step'not in g.user.extra:
            return redirect(url_for('mobile.m_home'))
        else:
            error = u'改账户不可用，请到网站端处理'
    return render_template('/mobile/login.html', error=error)

@module.route('/m/selectchild/', methods=['GET','POST'])
def m_selectchild():
    error = None
    if g.user and g.user.isparent:
        children = g.user.children
        print '#'*100+'%s'%len(children)
        if len(children) == 1:
            child = children[0]
            session['parent_id'] = g.user.user_id
            session['user_id'] = child.user_id
            return redirect(url_for('mobile.m_home'))
    else:
        return redirect(url_for('mobile.m_home'))
    if request.method == 'POST':
        user_id = request.form.get('user_id',None)
        if not user_id:
            error = u'请选择您其中的一个孩子'
        else:
            session['parent_id'] = g.user.user_id
            session['user_id'] = user_id
            return redirect(url_for('mobile.m_home'))
    return render_template('/mobile/selectchild.html',error = error)

@module.route('/m/home/', methods=['GET','POST'])
@m_login_required
def m_home():
    return render_template('/mobile/home.html')

@module.route('/m/task/', methods=['GET','POST'])
@m_login_required
def m_task():
    user = g.user
    if user.isteacher:
        page = int(request.args.get("page","1"))# 当前页
        query = Task.teacher_task_query(user,filter_key='task')
        count = query.count()
        tasklist = query.offset(page*10 - 10).limit(10).all()# 查询的具体数据
        pagination = Pagination(query,page,10,count,tasklist)# 每页30个
        result = []
        for task in pagination.items:
            data=f.teacher_task_summary(task)
            data.update(task.tojson())
            userjson = user.tojson()
            data.update({'teacher':userjson})
            data.update({'user':userjson})
            result.append(data)
        
        weekdate = datetime.now() + timedelta(6 - datetime.today().weekday())
        weekday = weekdate.strftime("%Y/%m/%d")
        return render_template('/mobile/task.html',
                            result=result,
                            pagination=pagination,
                            page=page,
                            weekday = weekday,
                            back='index',
                            title=u'作业')
    
    if user.isstudent or user.isparent:
        return redirect('/m/task/notreaded/')
    
    return render_template('/mobile/task.html')

@module.route('/m/task/readed/', defaults={'filter':'readed'})
@module.route('/m/task/notreaded/', defaults={'filter':'notreaded'})
@module.route('/m/task/writing/', defaults={'filter':'writing'})
@m_login_required
def m_task_filter(filter):
    """左侧导航上 已完成和未完成作业显示"""
    user = g.user
    if user.isteacher:
        works,page = f.pages(f.teacher_works,user,filter_key=filter)
        return render_template('/mobile/works.html',works=works,page=page,back='back',title=u'作业')
    if user.isparent:
        user_id = session['child_id']
        student = f.load_user(user_id)
        
    if user.isstudent:
        student = user
        
    if user.isstudent or user.isparent:
        if filter == 'writing':
            page = int(request.args.get("page","1"))# 当前页
            query = Task.student_task_query(student,filter_key='writing')
            count = query.count()
            tasklist = query.offset(page*10 - 10).limit(10).all()# 查询的具体数据
            pagination = Pagination(query,page,10,count,tasklist)# 每页30个
            parent = g.parent
            result = []
            for taskbox,task in pagination.items:
                data={}
                data.update(task.tojson())
                data.update(isconfirm=True if taskbox.confirm == 1 else False)
                data.update(taskbox_id=taskbox.id)
                data.update({'teacher':task.owner.tojson()})
                data.update({'student':user.tojson()})
                if parent:
                    data.update({'parent':parent.tojson()})
                    data.update({'user':parent.tojson()})
                else:
                    data.update({'parent':user.parent.tojson()})
                    data.update({'user':user.tojson()})
                data.update(f.teacher_task_summary(task))
                result.append(data)
            return render_template('/mobile/task.html',
                                result=result,
                                pagination=pagination,
                                page=page,
                                back='back',
                                title=student.nickname + u' -- 笔头作业')
        else:
            if filter == 'notreaded':
                title=u'当前作业'
                filter_key='notreaded'
            if filter == 'readed':
                title=u'已完成作业'
                filter_key='readed'
                
            parent = g.parent.tojson()
            page = int(request.args.get("page","1"))# 当前页
            query = Works.student_works_query(student, filter_key=filter_key)
            count = query.count()
            workslist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
            pagination = Pagination(query,page,30,count,workslist)# 每页30个
            workslist = []
            for taskbox,task,works in pagination.items:
                teacher = f.load_user(task.creator)
                worksjson = works.tojson() if works else None
                data = {'works':worksjson}
                userjson = student.tojson()
                data.update(userjson)
                data.update(userjson)
                data.update(teacher = teacher.tojson())
                data.update(task = task.tojson(worksjson))
                workslist.append(data)
            return render_template('/mobile/works.html',
                                    workslist = workslist,
                                    pagination = pagination,
                                    parent = parent,
                                    works=works,
                                    page=page,
                                    back='back',
                                    title=title)


@module.route('/m/works/<task_id>/', methods=['GET','POST'])
@m_login_required
def m_works(task_id):
    user = g.user
    if user.isteacher:
        task = m.session.query(Task).filter(Task.task_id == task_id).first()
        title = None
        if task:
            title = task.task_content
            works,page = f.pages(f.teacher_works,user,filter_key='notreaded',task_id=task_id)
        else:
            works,page = None,None
        return render_template('/mobile/works.html',works=works,page=page,back='back',title = title)
    return render_template('/mobile/works.html')


@module.route('/m/notify/', methods=['GET','POST'])
@m_login_required
def m_notify():
    """通知"""
    user = g.user
    if user.isteacher:
        page = int(request.args.get("page","1"))# 当前页
        query = Task.teacher_task_query(user,filter_key='notify')
        count = query.count()
        tasklist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
        pagination = Pagination(query,page,30,count,tasklist)# 每页30个
        result = []
        for task in pagination.items:
            data=f.teacher_task_summary(task)
            data.update(task.tojson())
            userjson = user.tojson()
            data.update({'teacher':userjson})
            data.update({'user':userjson})
            result.append(data)
        return render_template('/mobile/notify.html',result=result,pagination=pagination,page=page,back='back',title = u'通知')
    
    if user.isparent:
        user_id = session['child_id']
        student = f.load_user(user_id)
        
    if user.isstudent:
        student = user
    
    if user.isstudent or user.isparent:
        title = u'通知'
        if user.isparent:
            title = student.nickname + u' -- 通知'
        page = int(request.args.get("page","1"))# 当前页
        query = Task.student_task_query(student,filter_key='notify')
        count = query.count()
        tasklist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
        pagination = Pagination(query,page,30,count,tasklist)# 每页30个
        
        result = []
        for taskbox,task in pagination.items:
            data={}
            data.update(task.tojson())
            data.update(isconfirm=True if taskbox.confirm == 1 else False)
            data.update(taskbox_id=taskbox.id)
            data.update({'teacher':task.owner.tojson()})
            data.update({'user':user.tojson()})
            data.update(f.teacher_task_summary(task))
            result.append(data)
        return render_template('/mobile/notify_student.html',result=result,pagination=pagination,page=page,back='back',title = title)
    

@module.route('/m/class/<class_id>/', methods=['GET','POST'])
@m_login_required
def m_class(class_id = None):
    if class_id:
        classgrade = m.session.query(Classgrade).filter(Classgrade.class_id == class_id).first()
        return render_template('/mobile/members.html', classgrade = classgrade, back = 'back',title = u'班级')
    else:
        return render_template('/mobile/class.html')

@module.route('/m/favor/', methods=['GET','POST'])
@m_login_required
def m_favor():
    return render_template('/mobile/favor.html')

@module.route('/m/setting/', methods=['GET','POST'])
@m_login_required
def m_setting():
    return render_template('/mobile/setting.html')

@module.route('/m/logout/')
def logout():
    session.pop('user_id', None)
    session.pop('parent_id', None)
    return redirect('/m/')
