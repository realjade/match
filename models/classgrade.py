# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
import time
from sqlalchemy import desc, asc


classgrade = Table("classgrade", metadata, autoload=True)
classgrade_task = Table("classgrade_task",metadata, autoload=True)
classgrade_demand = Table('classgrade_demand',metadata, autoload = True)
demand = Table('demand',metadata, autoload = True)


class Classgrade(Base, buildmixin('extra')):
    __table__ = classgrade
    
    @property
    def students(self):
        """班级内所有学生"""
        from models.user import User, UserClass
        query = session.query(User)
        query = query.join(UserClass, User.user_id == UserClass.user_id)
        query = query.filter(UserClass.class_id == self.class_id)
        query = query.filter(UserClass.is_creator == 0)
        query = query.filter(UserClass.identity == 0)
        query = query.filter(UserClass.valid == 1)
        return query.all()
    
    @property
    def newstudents(self):#TODO delete
        from models.user import UserClass
        return session.query(UserClass).filter(UserClass.class_id == self.class_id,UserClass.is_creator == 0).all()
    
    @property
    def studentcount(self):
        """班级内的学生数量"""
        from models.user import User, UserClass
        query = session.query(UserClass).filter(UserClass.class_id == self.class_id)
        query = query.join(User,User.user_id == UserClass.user_id)
        query = query.filter(User.is_student == 1)
        return query.count()
    
    @property
    def teachercount(self):#TODO delete
        """班级内的老师数量"""
        from models.user import User, UserClass
        query = session.query(UserClass).filter(UserClass.class_id == self.class_id)
        query = query.join(User,User.user_id == UserClass.user_id)
        query = query.filter(User.is_teacher == 1)
        return query.count()
    
    @property
    def teacher(self):
        """查看当前班级老师 同creator"""
        from models.user import User, UserClass
        query = session.query(User)
        query = query.join(UserClass,UserClass.user_id == User.user_id)
        query = query.filter(UserClass.class_id == self.class_id)
        query = query.filter(UserClass.valid == 1)
        query = query.filter(UserClass.is_creator == 1)
        return query.first()
    
    @property
    def creator(self):#TODO json
        """创建班级老师信息"""
        user = self.teacher
        if user:
            return {'nickname':user.nickname,'mobile':user.mobile,'user_id':user.user_id}
        else:
            return {}
    
    @property
    def get_demand(self):
        """班级内最新的新学期新要求"""
        query = session.query(Demand)
        query = query.join(ClassDemand,Demand.demand_id == ClassDemand.demand_id)
        query = query.filter(ClassDemand.class_id == self.class_id)
        query = query.order_by(ClassDemand.created.desc())
        demand = query.first()
        return demand
    
    def init_taskbox(self,user):
        """用户加入班级时 初始化在当前班级的作业"""
        from models.task import Task, Taskbox
        curtime = int(time.time()*1000)
        ctquery = session.query(ClassTask, Task)
        ctquery = ctquery.filter(ClassTask.class_id == self.class_id)
        ctquery = ctquery.join(Task, ClassTask.task_id == Task.task_id)
        classtasks = ctquery.filter(Task.dead_line > curtime).all()
        
        for task in classtasks:
            query = session.query(Taskbox).filter(Taskbox.user_id == user.user_id)
            query = query.filter(Taskbox.class_id == self.class_id)
            taskbox = query.filter(Taskbox.task_id == task.Task.task_id).first()
            if not taskbox:
                taskbox = Taskbox(user_id = user.user_id, class_id = self.class_id, task_id = task.Task.task_id, confirm = 0,
                    created= int(time.time()*1000), updated=int(time.time()*1000))
                session.add(taskbox)
        session.commit()
    
    def tojson(self,dt):
        from lib import filters as ft
        result = {
                'class_name':self.class_name,
                'class_id':self.class_id,
                'email':self.email,
                'description':self.extra.get('description'),
                'creator':self.creator,
                'created':ft.format_datetime(self.created),
                'updated':self.updated,
                'school':self.school,
                'description':self.extra.get('description'),
                'tname':self.creator.get('nickname',''),
                'class_invitation':True,
                'studentcount':self.studentcount,
                }
        result.update(dt)
        return result

class ClassTask(Base,buildmixin('extra')):
    __table__ = classgrade_task


class ClassDemand(Base):
    __table__ = classgrade_demand


class Demand(Base):
    __table__ = demand
    
    @property
    def classes(self):
        query = session.query(Classgrade)
        query = query.join(ClassDemand,ClassDemand.class_id == Classgrade.class_id)
        return query.filter(ClassDemand.demand_id == self.demand_id).all()
    
    @property
    def teacher(self):
        from models.user import User
        query = session.query(User)
        user = query.filter(User.user_id == self.creator).first()
        return user

