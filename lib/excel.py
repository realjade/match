# -*- coding: utf-8 -*-
import xlwt,xlrd
from models.tables import *
import StringIO
from flask import g
from datetime import datetime

def export(classids):
    wb = xlwt.Workbook()
    videosheet = wb.add_sheet(u'视频作业')
    writesheet = wb.add_sheet(u'笔头作业')
    classgrades = session.query(Classgrade).filter(Classgrade.class_id.in_(classids)).all()
    tasks = session.query(ClassTask,Task).filter(ClassTask.class_id.in_(classids))\
        .outerjoin(Task,Task.task_id == ClassTask.task_id).filter(Task.creator == g.user.user_id).all()
    tasks = map(lambda x:x.Task,tasks)
    #tasks = session.query(Task).filter(Task.task_id.in_(taskids)).all()
    videotasks = filter(lambda x:x.task_type == 1,tasks)
    writetasks = filter(lambda x:x.task_type == 2,tasks)
    videotaskids = map(lambda x:x.task_id,videotasks)
    writetaskids = map(lambda x: x.task_id,writetasks)
    
    videoworks = session.query(Taskbox,Works, User) \
        .filter(Taskbox.class_id.in_(classids), Taskbox.task_id.in_(videotaskids),Taskbox.works_id != None) \
        .outerjoin(User,User.user_id == Taskbox.user_id) \
        .outerjoin(Works, Taskbox.works_id == Works.works_id).all()
    init_summary(classgrades,videotasks,videoworks,videosheet)
    
    writeworks = session.query(Taskbox,Works,User)\
        .filter(Taskbox.class_id.in_(classids),Taskbox.task_id.in_(writetaskids),Taskbox.works_id != None)\
        .outerjoin(User,User.user_id == Taskbox.user_id)\
        .outerjoin(Works, Taskbox.works_id == Works.works_id).all()
    init_summary(classgrades,writetasks,writeworks,writesheet)
    
    file = StringIO.StringIO()
    wb.save(file)
    file.seek(0)
    return file

def init_summary(classgrades,tasks,works,sheet):
    dclass = dict(map(lambda x:(x.class_id,x.class_name),classgrades))
    dtask = dict(map(lambda x:(x.task_id,x),tasks))
    dworks = {}
    duser = {}
    for w in works:
        if w.User.user_id not in duser:
            duser[w.User.user_id] = [w]
        else:
            duser[w.User.user_id].append(w)
        if w.Taskbox.class_id not in dworks:
            dworks[w.Taskbox.class_id] = [w]
        else:
            dworks[w.Taskbox.class_id].append(w)
    font = xlwt.Font()
    font.name = 'Times New Roman'
    font.bold = True
    align = xlwt.Alignment()
    align.wrap = True
    align.horz = xlwt.Alignment.HORZ_LEFT
    align.vert = xlwt.Alignment.VERT_TOP
    style = xlwt.XFStyle()
    style.font = font
    style.alignment = align
    start = 1
    end = 2
    linenum = 1
    for dt in dtask:
        sheet.write_merge(0,0,start,end,dtask.get(dt).task_content,style)
        sheet.write(1,start,u'完成',style)
        sheet.write(1,start+1,u'评分',style)
        start += 2
        end += 2
    end -= 2
    linenum += 1
    for c in classgrades:
        users = dworks.get(c.class_id)
        if not users:
            continue
        sheet.write_merge(linenum,linenum,0,end,c.class_name)
        linenum += 1
        for user in users:
            sheet.write(linenum,0,user.User.nickname)
            for tasknum in range(len(tasks)):
                #works loop
                for du in duser[user.User.user_id]:
                    if tasks[tasknum].task_id == user.Taskbox.task_id:
                        finish = u'未完成'
                        if user.Works.teacher_readed:
                            finish = u'完成'
                        sheet.write(linenum,1+2*tasknum,finish)
                        sheet.write(linenum,2+2*tasknum,user.Works.star)
                        break
            linenum += 1


def test():
    g.user = session.query(User).filter(User.email == 'ls@ls.com').first()
    tasks = session.query(Task).filter(Task.creator == g.user.user_id).all()
    taskids = map(lambda x:x.task_id,tasks)
    classgrades = session.query(UserClass).filter(UserClass.user_id == g.user.user_id).all()
    classids = map(lambda x:x.class_id,classgrades)
    export(classids,taskids)
