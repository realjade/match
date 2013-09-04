# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import render_template, g, request, url_for, redirect
from lib import const, videoworks
import models as m
from models.tables import Taskbox,TimeLine, Works, IndexVideo, Video
from datetime import datetime, timedelta
import time
from lib.wrappers import login_required, jsonify, parent_required
import lib.functions as f
import lib.datawrappers as dw
from models.tables import Task
from flask.ext.sqlalchemy import Pagination
from sqlalchemy import desc, asc, or_


module = Blueprint('task', __name__)


@module.route('/task/', methods=['GET'])
@login_required
def task():
    user = g.user
    if user.isteacher:
        page = int(request.args.get("page","1"))# 当前页
        weekdate = datetime.now() + timedelta(6 - datetime.today().weekday())
        weekday = weekdate.strftime("%Y/%m/%d")
        
        term = f.SchoolTerm()
        query = m.session.query(Task).filter(Task.creator == user.user_id)
        query = query.filter(Task.created >= term.currentterm)
        query = query.filter(Task.task_type.in_((1,2,4,5)))
        count = query.count()
        query = query.order_by(desc(Task.updated))
        tasklist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
        pagination = Pagination(query,page,30,count,tasklist)# 每页10个
        
        result = []
        for task in pagination.items:
            data=f.teacher_task_summary(task)
            data.update(dw.wrap_task(task))
            data.update({'teacher':dw.wrap_user(user)})
            data.update({'user':dw.wrap_user(user)})
            result.append(data)
        
        return render_template('/task/teacher/task.html',
                    page=page,
                    pagination = pagination,
                    result = result,
                    tab = 'task',
                    weekday = weekday,
                    today = (datetime.now()+timedelta(1)).strftime("%Y/%m/%d"))
    
    if user.isstudent:
        return redirect('/task/notreaded/')
    
    if user.isparent:
        if user.children:
            return redirect('/task/notreaded/%s/' % user.children[0])
        return redirect(url_for('home.home'))


@module.route('/task/readed/', defaults={'filter':'readed'})
@module.route('/task/notreaded/', defaults={'filter':'notreaded'})
@login_required
def task_filter(filter):
    """已经批改 未批改 笔头作业"""
    page = int(request.args.get("page","1"))# 当前页
    term = f.SchoolTerm()
    user = g.user
    if user.isteacher:
        query = m.session.query(Taskbox,Task,Works).filter(Taskbox.works_id != None)
        query = query.join(Task,Taskbox.task_id == Task.task_id)
        query = query.filter(Task.created > term.currentterm)
        query = query.filter(Task.creator == user.user_id)
        query = query.join(Works,Taskbox.works_id == Works.works_id)
        query = query.filter(Works.parent_approval != 0)
        query = query.order_by(Task.created.desc(),Works.updated.desc())
        if filter == 'notreaded':
            query = query.filter(Works.teacher_readed == 0)
        if filter == 'readed':
            query = query.filter(Works.teacher_readed == 1)
        count = query.count()
        taskboxlist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
        pagination = Pagination(query,page,30,count,taskboxlist)# 每页10个
        result = []
        for taskbox, task, works in pagination.items:
            student = f.load_user(taskbox.user_id)
            data = {'works':dw.wrap_work(works)}
            data.update(student = dw.wrap_user(student))
            data.update(parent = dw.wrap_user(student.parent))
            data.update(teacher = dw.wrap_user(user))
            data.update(user = dw.wrap_user(user))
            if works:
                extra = data['works']
            data.update(task = dw.wrap_task(task,extra = {'works':extra}))
            result.append(data)
            
        return render_template('/task/task_works.html',
                                page=page,
                                pagination = pagination,
                                result = result,
                                tab = 'task',
                                subtab = filter)
    
    if user.isstudent:
        if filter == 'notreaded' or filter == 'readed':
            query = m.session.query(Taskbox,Task,Works)
            query = query.filter(Taskbox.user_id == user.user_id)
            query = query.join(Task,Taskbox.task_id == Task.task_id)
            query = query.filter(Task.created > term.currentterm)
            query = query.filter(Task.task_type.in_((1,4,5)))

            if filter == 'notreaded':
                or_filter = or_(Taskbox.works_id == None,
                                Works.teacher_readed == 0,
                                Works.redo == 1)
                query = query.outerjoin(Works,Taskbox.works_id == Works.works_id).filter(or_filter)
                query = query.filter(Taskbox.class_id.in_(user.new_classgrades))
            if filter == 'readed':
                query = query.join(Works,Taskbox.works_id == Works.works_id)
                query = query.filter(Works.teacher_readed == 1)
                query = query.filter(Works.redo == 0)
            query = query.order_by(Task.created.desc())
            count = query.count()
            
            taskboxlist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
            pagination = Pagination(query,page,30,count,taskboxlist)# 每页10个
            
            result = []
            for taskbox, task, works in pagination.items:
                teacher = f.load_user(task.creator)
                data = {'works':dw.wrap_work(works)}
                data.update(student = dw.wrap_user(user))
                data.update(parent = dw.wrap_user(user.parent))
                data.update(user = dw.wrap_user(user))
                data.update(teacher = dw.wrap_user(teacher))
                extra = None
                if works:
                    extra = data['works']
                data.update(task = dw.wrap_task(task,extra = {'works':extra}))
                data.update(f.teacher_task_summary(task))
                result.append(data)
            videos = videoworks.load_nottasK_videos(user.user_id)
            return render_template('/task/task_works.html',
                                        pagination=pagination,
                                        result = result,
                                        page=page,
                                        videos = videos,
                                        tab = 'task',
                                        subtab = filter)
    
    if user.isparent:
        if user.children:
            return redirect('/task/%s/%s/' % (filter,user.children[0]))
        return redirect(url_for('home.home'))


@module.route('/task/writing/')
@parent_required
def task_writing():
    if user.children:
        return redirect('/task/%s/%s/' % (filter,user.children[0]))
    return redirect(url_for('home.home'))


@module.route('/notify/', methods=['GET'])
@module.route('/notify/all/<childid>/', methods=['GET'])
@login_required
def notify(childid = None):
    """通知"""
    page = int(request.args.get("page","1"))# 当前页
    user = g.user
    term = f.SchoolTerm()
    if user.isteacher:
        query = m.session.query(Task).filter(Task.creator == user.user_id)
        query = query.filter(Task.task_type ==3)
        query = query.filter(Task.created > term.currentterm)
        count = query.count()
        query = query.order_by(desc(Task.updated))
        tasklist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
        pagination = Pagination(query,page,30,count,tasklist)# 每页30个
        result = []
        for task in pagination.items:
            data=f.teacher_task_summary(task)
            data.update(dw.wrap_task(task))
            data.update({'teacher':dw.wrap_user(user)})
            data.update({'user':dw.wrap_user(user)})
            result.append(data)
        return render_template('/task/teacher/notify.html',
                                        result=result,
                                        page=page,
                                        pagination = pagination,
                                        tab = 'notify')
        
    if user.isstudent:
        query = m.session.query(Taskbox,Task)
        query = query.filter(Taskbox.user_id == user.user_id)
        query = query.join(Task,Taskbox.task_id == Task.task_id)
        query = query.filter(Task.task_type ==3)
        query = query.filter(Task.created > term.currentterm)
        query = query.order_by(desc(Task.updated))
        count = query.count()
        taskboxlist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
        pagination = Pagination(query,page,30,count,taskboxlist)# 每页30个)
        
        result = []
        for taskbox,task in pagination.items:
            data={}
            data.update(dw.wrap_task(task))
            data.update(isconfirm=True if taskbox.confirm == 1 else False)
            data.update(taskbox_id=taskbox.id)
            data.update({'teacher':dw.wrap_user(f.load_user(task.creator))})
            data.update({'student':dw.wrap_user(user)})
            data.update({'parent':dw.wrap_user(user.parent)})
            data.update({'user':dw.wrap_user(user)})
            data.update(f.teacher_task_summary(task))
            result.append(data)
        
        return render_template('/task/parent/notify.html',
                                            result=result,
                                            pagination = pagination,
                                            page=page,
                                            tab = 'notify',)
    if user.isparent:
        child = f.load_user(childid)
        parent = user
        
        query = m.session.query(Taskbox,Task)
        query = query.filter(Taskbox.user_id == child.user_id)
        query = query.join(Task,Taskbox.task_id == Task.task_id)
        query = query.filter(Task.task_type ==3)
        query = query.filter(Task.created > term.currentterm)
        query = query.order_by(desc(Task.updated))
        count = query.count()
        taskboxlist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
        pagination = Pagination(query,page,30,count,taskboxlist)# 每页30个)
        
        result = []
        for taskbox,task in pagination.items:
            data={}
            data.update(dw.wrap_task(task))
            data.update(isconfirm=True if taskbox.confirm == 1 else False)
            data.update(taskbox_id=taskbox.id)
            data.update({'teacher':dw.wrap_user(f.load_user(task.creator))})
            data.update({'student':dw.wrap_user(child)})
            data.update({'parent':dw.wrap_user(parent)})
            data.update({'user':dw.wrap_user(parent)})
            data.update(f.teacher_task_summary(task))
            result.append(data)
            
        return render_template('/task/parent/notify.html',
                                        result=result,
                                        pagination = pagination,
                                        page=page,
                                        tab = 'child',
                                        subtab = childid,
                                        subsubtab = 'notify')


@module.route('/api/task/confirm/', methods=['POST'])
@jsonify
@login_required
def api_task_confirm():
    """家长和学员确认作业 笔头和通知"""#TODO 未加身份识别
    taskbox_id = request.form.get('taskbox_id',None)
    if not taskbox_id:
        return const.INVALID_PARAMS
    taskbox = m.session.query(Taskbox).filter(Taskbox.id == taskbox_id).first()
    if not taskbox:
        return const.HOMEWORK_NOT_EXIST
    taskbox.confirm = 1;
    m.session.commit()
    return 'ok'


@module.route('/approval/', methods=['POST'])
@login_required
def approval():
    """家长和学员自我点评"""
    works_id = request.form.get('works_id','')
    if not works_id:
        return f.failed(*const.HANDIN_NOT_EXIST)
    w = m.session.query(Works).filter(Works.works_id == works_id).first()
    if not w:
        return f.failed(*const.HANDIN_NOT_EXIST)
    if(w.user_id not in g.user.extra.get('children',[])) and (w.user_id != g.user.user_id):
        return f.failed(*const.HANDIN_NOT_YOURS)
    if w.teacher_readed == 1:
        return f.failed(*const.HOMEWORK_HASCORRECT)
        
    t = m.session.query(Taskbox, Task).filter(Taskbox.works_id==works_id) \
    .join(Task,Task.task_id == Taskbox.task_id).first()
    timeline = TimeLine(event='works.approval', user_id = g.user.user_id, task_id = t.Task.task_id,
        works_id = w.works_id,class_id = t.Taskbox.class_id,to_user_id = w.user_id,
        created = int(time.time()*1000), updated = int(time.time()*1000))
    timeline.extra['teacher_id'] = t.Task.creator
    m.session.add(timeline)
    comment = request.form.get('comment','')
    w.parent_comment = comment
    w.parent_approval =1
    w.updated = int(time.time()*1000)
    if t.Task.task_id == u"4000000000000":
        # 如果是系统发送的自我介绍作业 直接评定
        w.teacher_readed = 1
        w.teacher_comment = u"Excellent!太棒了！"
        w.star = 10
    
    m.session.commit()
    return f.succeed('ok')
