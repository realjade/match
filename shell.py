#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Creates shell
"""
import sys
import os
p = os.path.dirname(os.path.abspath(__file__))

from werkzeug import script

from vself import app
from models import metadata, session
import models as m
import lib.functions as f
from models.tables import *
import views.admin as adm
import lib.utils as ut
import time
from lib import videoworks,excel
from sqlalchemy import or_

ctx = app.test_request_context()

def make_shell():
    return dict(globals())

def ctx_push():
    ctx.push()

def ctx_pop():
    ctx.pop()
    
def add_admin(emailormobile):
    user = session.query(User).filter(or_(User.email == emailormobile,User.mobile == emailormobile)).first()
    if not user:
        raise
    admin = Admin(admin_id = ut.create_admin_id(),user_id = user.user_id,created = time.time()*1000,updated = time.time()*1000)
    session.add(admin)
    session.commit()

def load_user_classgrades(user_id):
    classes = m.session.query(UserClass, Classgrade)\
        .filter(UserClass.user_id == user_id, UserClass.valid == 1)\
        .outerjoin(Classgrade, Classgrade.class_id == UserClass.class_id)\
        .all()
    return classes

def update_task():
    tasks = m.session.query(Task).filter(Task.dead_line == None).all()
    for task in tasks:
        print task.task_id
        task.dead_line = 1348185600000
    m.session.commit()


def update_user_task():
    curtime = int(time.time()*1000)
    students = m.session.query(User).filter(User.is_student == 1).all()
    for user in students:
        classgrades = load_user_classgrades(user.user_id)
        for classgrade in classgrades:
            classgrade = classgrade.Classgrade
            classtasks = m.session.query(ClassTask, Task).filter(ClassTask.class_id == classgrade.class_id) \
                    .join(Task, ClassTask.task_id == Task.task_id) \
                    .filter(Task.dead_line > curtime).all()
            for task in classtasks:
                curtask = m.session.query(Taskbox).filter(Taskbox.user_id == user.user_id, Taskbox.task_id == task.Task.task_id, Taskbox.class_id == classgrade.class_id).first()
                if not curtask:
                    print 'add taskbox', user.nickname, classgrade.class_name, task.Task.task_content
                    taskbox = Taskbox(user_id = user.user_id, class_id = classgrade.class_id, task_id = task.Task.task_id, confirm = 0,
                        created= int(time.time()*1000), updated=int(time.time()*1000))
                    m.session.add(taskbox)
        m.session.commit()

def delete_user(emailormobile):
    u = m.session.query(User).filter(or_(User.email == emailormobile, User.mobile == emailormobile)).first()
    if not u: return
    if int(time.time() - u.updated/1000.0) <= 86400*7:
        print 'user logined in last 7 days, please remove manually'
        return
    videos = m.session.query(Video).filter(Video.user_id == u.user_id).all()
    if len(videos) > 0:
        print 'user has videos, please remove manually'
        return
    if u.isstudent:
        parent = u.parent
        if parent:
            children = d.extra.get('children', [])
            if u.user_id in children:
                children.pop(children.index(u.user_id))
                parent.extra.update(children = children)
        m.session.query(UserClass).filter(UserClass.user_id == u.user_id).delete()
        m.session.query(Taskbox).filter(Taskbox.user_id == u.user_id).delete()
        m.session.query(TimeLine).filter(or_(TimeLine.user_id == u.user_id, TimeLine.to_user_id == u.user_id)).delete()
        m.session.delete(u)
        m.session.commit()
    elif u.isparent:
        children = u.children
        for child in children:
            child.extra.pop('parent')
        m.session.query(TimeLine).filter(or_(TimeLine.user_id == u.user_id, TimeLine.to_user_id == u.user_id)).delete()
        m.session.delete(u)
        m.session.commit()
    elif u.isteacher:
        pass


def update_userguide():
    users = m.session.query(User).filter(User.is_student == 1).all()
    for u in users:
        parent = u.parent
        classgrades = u.classgrades
        if not parent and len(classgrades) == 0:
            print u.nickname, 'no parent', 'not join class', 'step 1'
            u.extra.update(guide_step = 1)
        elif not parent:
            print u.nickname, 'no parent', '|'.join(map(lambda x: x['class_name'], classgrades)), 'step 2'
            u.extra.update(guide_step = 2)
        else:
            pass #print u.nickname, 'parent:', u.parent.nickname, '|'.join(map(lambda x: x['class_name'], classgrades))
        m.session.commit()
    
if __name__ == "__main__":
    script.make_shell(make_shell, use_ipython=False)()
