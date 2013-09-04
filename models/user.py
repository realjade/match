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