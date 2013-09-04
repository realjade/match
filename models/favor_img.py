# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
import time
from sqlalchemy import desc, asc


teacher_favorimg = Table("teacher_favorimg",metadata,autoload=True)
teacher_favorimg_love = Table("teacher_favorimg_love",metadata,autoload=True)
teacher_favorimg_comment = Table("teacher_favorimg_comment",metadata,autoload=True)


class TeacherFavorImg(Base):
    __table__ = teacher_favorimg
    
    @property
    def user(self):
        from lib.functions import load_user
        return load_user(self.user_id)
    
    @property
    def classgrade(self):
        from models.classgrade import Classgrade
        return session.query(Classgrade).filter(self.class_id == Classgrade.class_id).first()


class TeacherFavorImgLove(Base):
    __table__ = teacher_favorimg_love


class TeacherFavorImgComment(Base):
    __table__ = teacher_favorimg_comment
    
    @property
    def reply(self):
        return session.query(TeacherFavorImgComment).filter(TeacherFavorImgComment.id == self.reply_id).first()
    
    @property
    def user(self):
        from lib.functions import load_user
        return load_user(self.user_id)

