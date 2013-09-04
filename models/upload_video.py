# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
import time
from sqlalchemy import desc, asc


favvideocreate = Table('favvideocreate',metadata, autoload = True)
favvideo = Table('favvideo',metadata, autoload = True)
favvideouser = Table('favvideouser',metadata, autoload = True)
favvideobox = Table('favvideobox',metadata, autoload = True)
favvideoitem = Table('favvideoitem',metadata, autoload = True)
favvideo_comment = Table('favvideo_comment',metadata, autoload = True)



class FavVideoCreate(Base):
    __table__ = favvideocreate
    
    @property
    def video(self):
        from models.video import Video
        return session.query(Video).filter(Video.video_id == FavVideoCreate.video_id).first()

class FavVideo(Base):
    __table__ = favvideo
    
    @property
    def user(self):
        from lib.functions import load_user
        return load_user(self.user_id)
    
    @property
    def item(self):
        return session.query(FavVideoItem).filter(FavVideoItem.favvideo_id == self.favvideo_id).first()
    
    
    @property
    def classgrades(self):
        from models.classgrade import Classgrade
        query = session.query(Classgrade)
        query = query.join(FavVideoBox,FavVideoBox.class_id == Classgrade.class_id)
        query = query.filter(FavVideoBox.favvideo_id == self.favvideo_id)
        return query.all()
    
    @property
    def read(self):
        query = session.query(FavVideoUser)
        query = query.filter(FavVideoUser.favvideo_id == self.favvideo_id)
        query = query.filter(FavVideoUser.is_read == 1)
        return query.count()
    
    @property
    def noread(self):
        query = session.query(FavVideoUser)
        query = query.filter(FavVideoUser.favvideo_id == self.favvideo_id)
        query = query.filter(FavVideoUser.is_read == 0)
        return query.count()

class FavVideoUser(Base):
    __table__ = favvideouser
    
    @staticmethod
    def notread(child):
        """老师上传视频 小孩为观看的数量"""
        query = session.query(FavVideoUser)
        query = query.filter(FavVideoUser.user_id == child.user_id)
        query = query.filter(FavVideoUser.is_read == 0)
        return query.count()

class FavVideoBox(Base):
    __table__ = favvideobox

class FavVideoItem(Base):
    __table__ = favvideoitem
    
    @property
    def video(self):
        from models.video import Video
        return session.query(Video).filter(Video.video_id == self.video_id).first()

class FavVideoComment(Base):
    __table__ = favvideo_comment
    
    @property
    def reply(self):
        return session.query(FavVideoComment).filter(FavVideoComment.id == self.reply_id).first()
    
    @property
    def user(self):
        from lib.functions import load_user
        return load_user(self.user_id)

