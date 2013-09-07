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
    def isAdmin(self):
        """是否是管理员"""
        return self.isadmin == 1
    
    # 静态方法 与模型相关的功能性函数
    @staticmethod
    def get_user(mobile):
        """根据邮箱或者手机号 获取用户"""
        if ut.is_mobile(mobile):
            return session.query(User).filter(User.mobile == mobile).first()
        return None
    
    def tojson(self):
        import lib.filters as ft
        return {'id':self.id,
                'mobile':self.mobile,
                'nickname':self.nickname,
                'isadmin':self.isadmin,
                'gender':self.gender,
                'smallavatar': ft.avatar(self),
                'mediumavatar': ft.avatar(self,'medium'),
                'bigavatar': ft.avatar(self,'big'),
                'slogan':self.slogan,
                'height':self.height,
                'weight':self.mobile,
                'team_id':self.team_id,
                'role':self.role,
                'position':self.position
                }