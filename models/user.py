# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
import time
from werkzeug import check_password_hash, generate_password_hash
from sqlalchemy import desc, asc
from lib import utils as ut


user = Table("user", metadata, autoload=True)
passwordreset = Table('passwordreset',metadata, autoload = True)
mobilecode = Table('mobilecode',metadata, autoload = True)
user_classgrade = Table("user_classgrade",metadata, autoload=True)


class User(Base, buildmixin('extra')):
    __table__ = user
    
    def check_password_hash(self,password):
        """验证密码"""
        return check_password_hash(self.pw_hash,password)
    
    def generate_password_hash(self,password):
        """加密密码"""
        self.pw_hash = generate_password_hash(password)
    
    def __str__(self):
        return self.user_id
        
    @property
    def isteacher(self):
        """是否是老师"""
        return self.is_teacher != 0
    
    @property
    def isparent(self):
        """是否是家长"""
        return self.is_parent == 1
    
    @property
    def isstudent(self):
        """是否是学生"""
        return self.is_student != 0
    
    @property
    def course(self):
        """教师教学的科目 语文数学等"""
        return self.extra.get('course','') if self.isteacher else ''
    
    @property
    def profile(self):
        """记录个人信息 QQ phone number等 拓展个人设置"""
        return self.extra.get("profile",{})
    
    @property
    def child(self):
        """获取孩子信息"""
        children = self.extra.get('children',None)
        if children:
            return session.query(User).filter(User.user_id.in_(children)).first()
        return None
    
    @property
    def children(self):
        """所有子女"""
        children = self.extra.get('children',None)
        if children:
            return session.query(User).filter(User.user_id.in_(children)).all()
        else:
            return []
    
    @property
    def parent(self):
        """获取学生的父母"""
        parent = self.extra.get('parent',None)
        if parent:
            return session.query(User).filter(User.user_id == parent).first()
        return None
    
    def classgrade_model(self, class_id):
        from models.classgrade import Classgrade
        query = session.query(Classgrade)
        query = query.filter(Classgrade.class_id == class_id)
        query = query.join(UserClass, Classgrade.class_id == UserClass.class_id)
        query = query.filter(UserClass.user_id == self.user_id)
        query = query.filter(UserClass.valid == 1)
        classes = query.first()
        return classes
    
    
    def classgrades_model(self):
        from models.classgrade import Classgrade
        query = session.query(Classgrade)
        query = query.join(UserClass, Classgrade.class_id == UserClass.class_id)
        query = query.filter(UserClass.user_id == self.user_id)
        query = query.filter(UserClass.valid == 1)
        classes = query.all()
        return classes
    
    @property
    def classgrades(self):
        """查询老师和学生所在的班级 返回[{...}]"""
        from models.classgrade import Classgrade
        query = session.query(UserClass, Classgrade)
        query = query.filter(UserClass.user_id == self.user_id)
        query = query.filter(UserClass.valid == 1)
        query = query.outerjoin(Classgrade, Classgrade.class_id == UserClass.class_id)
        classes = query.all()
        return map(lambda x:{'class_name':x.Classgrade.class_name,'class_id':x.Classgrade.class_id,
                     'created':x.Classgrade.created,'updated':x.Classgrade.updated,
                     'joined':x.UserClass.created,'school':x.Classgrade.school},classes)
    
    @property
    def new_classgrades(self):
        """查询用户的班级id列表 包括家长"""
        if self.isparent:
            class_obj_list = []
            for child in self.children:
                class_obj_list.extend(child.classgrades)
            return list(set([cg["class_id"] for cg in class_obj_list]))
        else:
            return [cg["class_id"] for cg in self.classgrades]
    
    @property
    def indexdata(self):
        """左侧导航上 作业数量显示"""
        from models.task import Task
        if self.isteacher:
            notreaded = Task.teacher_notread_count(self)
            return {'notread':notreaded}
        
        if self.isstudent:
            from models.upload_video import FavVideoUser
            from models.upload_img import FavImgUser
            task_new = Task.student_new_count(self)
            task_todo = Task.student_todo_count(self)
            notify_new = Task.student_notify_count(self)
            task_writing = Task.student_writing_count(self)
            upload_video = FavVideoUser.notread(self)
            upload_img = FavImgUser.notread(self)
            return {"task_new" : task_new,
                    "task_todo" : task_todo,
                    "notify_new" : notify_new,
                    "task_writing" : task_writing,
                    "upload_video" : upload_video,
                    "upload_img" : upload_img}
    
    @property
    def first_demand(self):
        """新学期新要求显示"""
        from models.classgrade import Classgrade
        if self.new_classgrades:
            class_id = self.new_classgrades[0]
            classgrade = session.query(Classgrade).filter(Classgrade.class_id == class_id).first()
            return classgrade.get_demand
        return None
    
    @property
    def get_extra_guide(self):
        """guide记录教师的资格证等信息"""
        guide = self.extra.get("guide",None)
        if guide:
            from models.school import School
            guide['school'] = session.query(School).filter(School.school_id == guide.get('schoolid',None)).first()
        return guide
    
    @property
    def noticecount(self):
        """通知数量"""
        from models.admin import UserNotice
        query = session.query(UserNotice)
        query = query.filter(UserNotice.accept_user == self.user_id)
        query = query.filter(UserNotice.isread == 0)
        return query.count()
    
    # 静态方法 与模型相关的功能性函数
    @staticmethod
    def get_user(username):
        """根据邮箱或者手机号 获取用户"""
        if ut.is_email(username):
            return session.query(User).filter(User.email == username).one()
        elif ut.is_mobile(username):
            return session.query(User).filter(User.mobile == username).one()
        return None
    
    def tojson(self):
        import lib.filters as ft
        return {'user_id':self.user_id,
                'course':self.course,
                'isstudent':self.isstudent,
                'isteacher':self.isteacher,
                'isparent':self.isparent,
                'smallavatar': ft.avatar(self),
                'mediumavatar': ft.avatar(self,'medium'),
                'bigavatar': ft.avatar(self,'big'),
                'nickname':self.nickname,
                'email':self.email,
                'mobile':self.mobile,
                }


class Passwordreset(Base):
    __table__ = passwordreset


class MobileCode(Base):
    __table__ = mobilecode
    
    def vali(self,code):
        if self.code != code:
            return False
        if self.created +60*10*1000 >= time.time()*1000:
            return True
        else:
            return False


class UserClass(Base, buildmixin('extra')):
    __table__ = user_classgrade
