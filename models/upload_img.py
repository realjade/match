# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
import time
from sqlalchemy import desc, asc


favimgcreate = Table('favimgcreate',metadata, autoload = True)
favimg = Table('favimg',metadata, autoload = True)
favimguser = Table('favimguser',metadata, autoload = True)
favimgbox = Table('favimgbox',metadata, autoload = True)
favimgitem = Table('favimgitem',metadata, autoload = True)
favimg_comment = Table('favimg_comment',metadata, autoload = True)


class FavImgCreate(Base,buildmixin('extra')):
    __table__ = favimgcreate
    
    @property
    def thumbnail(self):
        thumbnail_path = self.extra.get("thumbnail_path",None)
        if thumbnail_path:
            return thumbnail_path
        else:
            return self.path

class FavImg(Base):
    __table__ = favimg
    
    @property
    def user(self):
        from lib.functions import load_user
        return load_user(self.user_id)
    
    @property
    def items(self,limit = 3):
        return session.query(FavImgItem).filter(FavImgItem.favimg_id == self.favimg_id).limit(limit).all()
    
    @property
    def classgrades(self):
        from models.classgrade import Classgrade
        query = session.query(Classgrade)
        query = query.join(FavImgBox,FavImgBox.class_id == Classgrade.class_id)
        query = query.filter(FavImgBox.favimg_id == self.favimg_id)
        return query.all()
    
    @property
    def read(self):
        query = session.query(FavImgUser)
        query = query.filter(FavImgUser.favimg_id == self.favimg_id)
        query = query.filter(FavImgUser.is_read == 1)
        return query.count()
    
    @property
    def noread(self):
        query = session.query(FavImgUser)
        query = query.filter(FavImgUser.favimg_id == self.favimg_id)
        query = query.filter(FavImgUser.is_read == 0)
        return query.count()

class FavImgUser(Base):
    __table__ = favimguser
    
    @staticmethod
    def notread(child):
        """老师上传图片 小孩为观看的数量"""
        query = session.query(FavImgUser)
        query = query.filter(FavImgUser.user_id == child.user_id)
        query = query.filter(FavImgUser.is_read == 0)
        return query.count()

class FavImgBox(Base):
    __table__ = favimgbox

class FavImgItem(Base,buildmixin('extra')):
    __table__ = favimgitem
    
    @property
    def thumbnail(self):
        thumbnail_path = self.extra.get("thumbnail_path",None)
        if thumbnail_path:
            return thumbnail_path
        else:
            return self.path

class FavImgComment(Base):
    __table__ = favimg_comment 
    
    @property
    def reply(self):
        return session.query(FavImgComment).filter(FavImgComment.id == self.reply_id).first()
    
    @property
    def user(self):
        from lib.functions import load_user
        return load_user(self.user_id)
