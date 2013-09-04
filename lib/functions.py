# -*- coding: utf-8 -*-
import os
import utils as ut
from flask import json, g, request, session
import models as m
from models.tables import User
from sqlalchemy import or_, func, distinct
from sqlalchemy import desc, asc
from sqlalchemy.orm import aliased
import time
from datetime import datetime
import types
import lib.filters as ft
import math
from cache import context_cached, redis_cached


def succeed(data):
    return json.dumps({"code":'0', "data":data})

def failed(code, message):
    return json.dumps({"code":code, "message":message})



###############################所有和角色没有关系或者通用的函数#########################################
#TODO 去掉老的分页在mobile.py中 然后删除
def paginated(query,column,count=-1, offset=-1, **kwargs):
    query = query.order_by(desc(column))
    if count > 0:
        query = query.limit(count)
    
    if offset > 0:
        query = query.offset(offset)

    result = query.all()
    return result

def pages(func, *args, **kwargs):
    page = {}
    curpage = request.args.get('page',1)
    if not curpage:
        curpage = 1
    curpage = int(curpage)
    count = 30
    kwargs.update(count=count)
    kwargs.update(offset=(curpage-1)*count)
    results,total = func(*args, **kwargs)
    page.update({'curpage':int(curpage),'pages':int(math.floor(total/count)+1),'total':int(total)})
    return results,page

###########################所有和角色没有关系或者通用的函数结束#################################


###########################老师相关#################################
def teacher_works(user,class_id = None,filter_key='',task_id = None,**kwargs):
    #TODO 删除该调用 使用models中works模型中的新方法
    query = m.session.query(Taskbox,Task,Works).filter(Taskbox.works_id != None)
    query = query.join(Task,Taskbox.task_id == Task.task_id)
    query = query.filter(Task.creator == user.user_id)
    query = query.join(Works,Taskbox.works_id == Works.works_id)
    query = query.filter(Works.parent_approval != 0)
    if task_id:
        query = query.filter(Task.task_id == task_id)
        query = query.order_by(Works.updated.desc())
    else:
        query = query.order_by(Task.created.desc(),Works.updated.desc())
    if class_id:
        query = query.filter(Taskbox.class_id == class_id)
    if filter_key == 'notreaded':
        query = query.filter(Works.teacher_readed == 0)
    if filter_key == 'readed':
        query = query.filter(Works.teacher_readed == 1)
    
    total = query.count()
    teacher_works = paginated(query, Taskbox.updated, **kwargs)
    
    result = []
    for taskbox, task, works in teacher_works:
        student = load_user(taskbox.user_id)
        data = {'works':dw.wrap_work(works)}
        data.update(student = dw.wrap_user(student))
        data.update(parent = dw.wrap_user(student.parent))
        data.update(teacher = dw.wrap_user(user))
        data.update(user = dw.wrap_user(user))
        if works:
            extra = data['works']
        data.update(task = dw.wrap_task(task,extra = {'works':extra}))
        result.append(data)
    return result,total


def teacher_task_summary(task=None):
    if task:
        confirmed = 0
        unconfirmed = 0
        unconmembers = []
        if task.iswriting or task.isnotify:
            confirmed  = m.session.query(Taskbox).filter(Taskbox.task_id == task.task_id,Taskbox.confirm == 1).count()
            unconfirmed = m.session.query(Taskbox).filter(Taskbox.task_id == task.task_id,Taskbox.confirm == 0).count()
            unconmembers = m.session.query(Taskbox,User,Classgrade).filter(Taskbox.task_id == task.task_id,Taskbox.confirm == 0) \
            .join(User,Taskbox.user_id == User.user_id).join(Classgrade,Taskbox.class_id == Classgrade.class_id).order_by(desc(Taskbox.class_id)).all()
        else:
            confirmed = m.session.query(Taskbox).filter(Taskbox.task_id == task.task_id,Taskbox.works_id != None).count()
            unconfirmed = m.session.query(Taskbox).filter(Taskbox.task_id == task.task_id,Taskbox.works_id == None).count()
            unconmembers = m.session.query(Taskbox,User,Classgrade).filter(Taskbox.task_id == task.task_id,Taskbox.works_id == None) \
            .join(User,Taskbox.user_id == User.user_id).join(Classgrade,Taskbox.class_id == Classgrade.class_id).order_by(desc(Taskbox.class_id)).all()
        wrapresult = {}
        for mem in unconmembers:
            classgrade = wrapresult.get(mem.Classgrade.class_name,None)
            if not classgrade:
                wrapresult.update({mem.Classgrade.class_name:[{'class_id':mem.Classgrade.class_id,'classname':mem.Classgrade.class_name,'user_id':mem.User.user_id,'nickname':mem.User.nickname}]})
            else:
                classgrade.append({'class_id':mem.Classgrade.class_id,'classname':mem.Classgrade.class_name,'user_id':mem.User.user_id,'nickname':mem.User.nickname})
        result =[]
        for key,value in wrapresult.items():
            result.append({'classname':key,'users':value})
        return {'statistics':{'confirmed':{'count':confirmed},'unconfirmed':{'count':unconfirmed,'users':result}}}


        
            
def task_summary(user):#TODO
    classes = m.session.query(UserClass,Classgrade)\
        .filter(UserClass.user_id == user.user_id,UserClass.identity == 1)\
        .outerjoin(Classgrade,Classgrade.class_id == UserClass.class_id).all()
    classids = map(lambda x:x.Classgrade.class_id,classes)
    students = m.session.query(UserClass)\
        .filter(UserClass.class_id.in_(classids),UserClass.identity == 0, UserClass.valid == 1).all()
    tasks = m.session.query(Task).filter(Task.creator == user.user_id).all()
    taskids = map(lambda x:x.task_id,tasks)
    dtasks = dict(map(lambda x:(x.task_id,x),tasks))
    studenttasks = m.session.query(Taskbox,Works)\
        .filter(Taskbox.task_id.in_(taskids))\
        .outerjoin(Works,Works.works_id == Taskbox.works_id).all()
    classtasks = m.session.query(ClassTask)\
        .filter(ClassTask.task_id.in_(taskids)).all()
    dclasses = dict(map(lambda x:(x.Classgrade.class_id,x.Classgrade.class_name),classes))
    dstudents = {}
    for student in students:
        if student.class_id in dstudents:
            dstudents[student.class_id] += 1
        else:
            dstudents[student.class_id] = 1
    dstudenttasks = {}
    for studenttask in studenttasks:
        if studenttask.Taskbox.class_id not in dstudenttasks:
            dstudenttasks[studenttask.Taskbox.class_id] = {}
        if studenttask.Taskbox.task_id in dstudenttasks:
            dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]['total'] += 1
        else:
            dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id] ={}
            dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]['total'] = 1
        if studenttask.Taskbox.works_id == None:
            if 'notsubmit' not in dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]:
                dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]['notsubmit'] = 1
            else:
                dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]['notsubmit'] += 1
        else:
            if 'submited' not in dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]:
                dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]['submited'] = 1
            else:
                dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]['submited'] += 1
            if studenttask.Works and studenttask.Works.teacher_readed:
                if 'readed' not in dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]:
                    dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]['readed'] = 1
                else:
                    dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]['readed'] += 1
            elif studenttask.Works and not studenttask.Works.teacher_readed:
                if 'notreaded' not in dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]:
                    dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]['notreaded'] = 1
                else:
                    dstudenttasks[studenttask.Taskbox.class_id][studenttask.Taskbox.task_id]['notreaded'] += 1
    ret = []
    for classid in classids:
        d = {'class_name':dclasses.get(classid),'class_id':classid,'studentcount':dstudents.get(classid)}
        ts = []
        sts = dstudenttasks.get(classid)
        if not sts:
            continue
        for taskid in taskids:
            dtask = sts.get(taskid)
            if dtask:
                ts.append({
                    'total':dtask.get('total',0),'notsubmit':dtask.get('notsubmit',0),
                    'submited':dtask.get('submited',0),'readed':dtask.get('readed',0),
                    'task_content':dtasks.get(taskid).task_content,'deadline':dtasks.get(taskid).dead_line,
                    'task_type':dtasks.get(taskid).task_type,'notreaded':dtask.get('notreaded',0)})
        d['tasks'] = ts
        ret.append(d)
    return ret
###########################老师相关结束#################################
###########################家长相关#################################
def add_student_account(puser,user):
    """在学生和父母的User表中extra扩展中保存相互间的关系"""
    user.extra.update({'parent':puser.user_id})
    children = puser.extra.get('children',[])
    if user.user_id not in children:
        children.append(user.user_id)
    puser.extra.update({'children':children})
    m.session.commit()
###########################家长相关结束#################################
@context_cached()
def load_user(user_id):
    return m.session.query(User).filter(User.user_id == user_id).first()


def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in set(['avi', 'flv', 'f4v', 'mp4', 'm4v', 'mkv', 
        'mov', '3gp', '3gp', '3g2', 'mpg', 'wmv', 'ts'])

def allowed_img_file(filename):
    extli = ['png', 'jpg', 'jpeg', 'gif']
    upextli = [ext.upper() for ext in extli]
    extli.extend(upextli)
    return '.' in filename and filename.rsplit('.', 1)[1] in set(extli)

def allowed_excel(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in set(['xls', 'xlsx'])


def time_filter(query, column, starttime, endtime):
    if starttime > 0:
        query = query.filter(column > starttime)
    if endtime > 0:
        query = query.filter(column < endtime)
    return query

