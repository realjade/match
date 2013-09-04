# -*- coding: utf-8 -*-
from flask import Blueprint
from lib import const, videoworks
import lib.datawrappers as dw
from flask import request, render_template, g
import models as m
from models.tables import Task, Works, Taskbox, TimeLine, IndexVideo, Video
import time
import lib.utils as ut
from lib.wrappers import login_required, parent_required, jsonify
import lib.functions as f
from flask.ext.sqlalchemy import Pagination
from sqlalchemy import desc, asc, or_


module = Blueprint('task_parent', __name__)


@module.route('/task/readed/<childid>/', defaults={'filter':'readed'})
@module.route('/task/notreaded/<childid>/',defaults={'filter':'notreaded'})
@parent_required
def task_parent(filter,childid):
    page = int(request.args.get("page","1"))# 当前页
    parent = g.user
    child = f.load_user(childid)
    term = f.SchoolTerm()
    query = m.session.query(Taskbox,Task,Works)
    query = query.filter(Taskbox.user_id == child.user_id)
    query = query.join(Task,Taskbox.task_id == Task.task_id)
    query = query.filter(Task.task_type.in_((1,4,5)))
    query = query.filter(Task.created > term.currentterm)
    if filter == 'notreaded':
        or_filter = or_(Taskbox.works_id == None,
                        Works.teacher_readed == 0,
                        Works.redo == 1)
        query = query.outerjoin(Works,Taskbox.works_id == Works.works_id).filter(or_filter)
        query = query.filter(Taskbox.class_id.in_(child.new_classgrades))
    if filter == 'readed':
        query = query.join(Works,Taskbox.works_id == Works.works_id)
        query = query.filter(Works.teacher_readed == 1)
        query = query.filter(Works.redo == 0)
    
    count = query.count()
    query = query.order_by(Task.created.desc())
    taskboxlist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
    pagination = Pagination(query,page,30,count,taskboxlist)# 每页30个
    
    result = []
    for taskbox, task, works in pagination.items:
        teacher = f.load_user(task.creator)
        data = {'works':dw.wrap_work(works)}
        data.update(student = dw.wrap_user(child))
        if not parent:
            data.update(parent = dw.wrap_user(child.parent))
            data.update(user = dw.wrap_user(child))
        else:
            data.update(parent = dw.wrap_user(parent))
            data.update(user = dw.wrap_user(parent))
        data.update(teacher = dw.wrap_user(teacher))
        extra = None
        if works:
            extra = data['works']
        data.update(task = dw.wrap_task(task,extra = {'works':extra}))
        data.update(f.teacher_task_summary(task))
        result.append(data)
    
    return render_template('/task/task_works.html',
                            page=page,
                            result = result,
                            pagination = pagination,
                            tab = 'child',
                            subtab=childid,
                            subsubtab = filter)

@module.route('/task/writing/<childid>/')
@parent_required
def task_parent_writing(childid):
    page = int(request.args.get("page","1"))# 当前页
    parent = g.user
    child = f.load_user(childid)
    term = f.SchoolTerm()
    query = m.session.query(Taskbox,Task)
    query = query.filter(Taskbox.user_id == child.user_id)
    query = query.join(Task,Taskbox.task_id == Task.task_id)
    query = query.filter(Task.created > term.currentterm)
    query = query.filter(Task.task_type ==2)
    query = query.order_by(desc(Task.updated))
    count = query.count()
    taskboxlist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
    pagination = Pagination(query,page,30,count,taskboxlist)# 每页30个
    
    result = []
    for taskbox,task in pagination.items:
        data={}
        data.update(dw.wrap_task(task))
        data.update(isconfirm=True if taskbox.confirm == 1 else False)
        data.update(taskbox_id=taskbox.id)
        data.update({'teacher':dw.wrap_user(f.load_user(task.creator))})
        data.update({'student':dw.wrap_user(child)})
        if parent:
            data.update({'parent':dw.wrap_user(parent)})
            data.update({'user':dw.wrap_user(parent)})
        else:
            data.update({'parent':dw.wrap_user(child.parent)})
            data.update({'user':dw.wrap_user(child)})
        data.update(f.teacher_task_summary(task))
        result.append(data)
        
    return render_template('/task/parent/writing.html',
                                pagination=pagination,
                                result = result,
                                page=page,
                                tab = 'child',
                                subtab=childid,
                                subsubtab = 'writing',)


@module.route('/handin/<task_id>/video/<video_id>/', methods=['GET','POST'])
@login_required
def handin_video(task_id, video_id):
    video = m.session.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        return f.failed(*const.VIDEO_NOT_EXIST)
    user = g.user
    user_id = video.user_id
    if user_id != g.user.user_id and user_id not in g.user.extra.get('children',[]):
        return f.failed(*const.HANDIN_NOT_YOURCHILD)
    tw = m.session.query(Taskbox,Task,Works).filter(Taskbox.task_id == task_id,Taskbox.user_id == user_id) \
    .join(Task,Taskbox.task_id == Task.task_id) \
    .outerjoin(Works,Taskbox.works_id == Works.works_id).first()
    if not tw:
        return f.failed(*const.HOMEWORK_NOT_EXIST)
    task = tw.Task
    taskbox = tw.Taskbox
    if not taskbox.works_id:
        #没有交过作业
        w = Works(
            user_id = user_id,
            works_id = ut.create_works_id(),
            parent_approval = 0,
            teacher_readed = 0,
            star = 0,
            created=int(time.time()*1000), updated=int(time.time()*1000)
            )
        w.content.update({'isvideo':True,'video_id':video_id})
        m.session.add(w)
        taskbox.works_id = w.works_id
        taskbox.updated = int(time.time()*1000)
        #表示该视频已经被占用
        iv = m.session.query(IndexVideo).filter(IndexVideo.video_id == video_id, IndexVideo.works_id == w.works_id).first()
        if not iv:
            iv = IndexVideo(
                works_id = w.works_id,
                video_id = video_id,
                task_id = task_id,
                created=int(time.time()*1000), updated=int(time.time()*1000)
                )
            m.session.add(iv)
    else:
        #交过作业情况
        w = m.session.query(Works).filter(Works.works_id == taskbox.works_id).first()
        iv = m.session.query(IndexVideo).filter(IndexVideo.video_id == w.content.get('video_id',''), IndexVideo.works_id == w.works_id).first()
        w.content.update({'video_id':video_id})
        w.updated = int(time.time()*1000)
        if iv:
            iv.video_id = video_id
    m.session.commit()
    teacher = f.load_user(task.creator)
    data = {'works':dw.wrap_work(w)}
    data.update(student = dw.wrap_user(f.load_user(user_id)))
    if user.isparent:
        data.update(parent = dw.wrap_user(user))
    else:
        data.update(parent = dw.wrap_user(user.parent))
    data.update(user = dw.wrap_user(user))
    data.update(teacher = dw.wrap_user(teacher))
    extra = {}
    extra['works'] = data['works']
    data.update(task = dw.wrap_task(task,extra = extra))
    data.update(video=dw.wrap_video(video))
    return f.succeed(data)
