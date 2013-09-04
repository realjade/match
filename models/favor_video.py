# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
import time
from sqlalchemy import desc, asc


teacher_favor = Table("teacher_favor",metadata,autoload=True)
teacher_favor_love = Table("teacher_favor_love",metadata,autoload=True)
teacher_favor_comment = Table("teacher_favor_comment",metadata,autoload=True)


class TeacherFavor(Base):
    __table__ = teacher_favor
    
    @property
    def user(self):
        from lib.functions import load_user
        return load_user(self.user_id)
    
    @property
    def classgrade(self):
        from models.classgrade import Classgrade
        return session.query(Classgrade).filter(self.class_id == Classgrade.class_id).first()
    
    @staticmethod
    def box():
        """网页右侧推荐视频"""
        from models.user import User
        from models.works import Works
        from models.video import Video, IndexVideo
        from models.task import Task
        from lib import functions as f
        term = f.SchoolTerm()
        user = g.user
        if user.isparent:
            class_ids = []
            for child in user.children:
                class_ids.extend(map(lambda x:x['class_id'], child.classgrades))
            class_ids = list(set(class_ids))
        else:
            class_ids = map(lambda x:x['class_id'], user.classgrades)
        
        if not class_ids:
            return []
        
        query = session.query(TeacherFavor, User, Works, Video, Task)
        if len(class_ids) == 1:
            query = query.filter(TeacherFavor.class_id == class_ids[0])
        else:
            query = query.filter(TeacherFavor.class_id.in_(class_ids))
        query = query.join(User, TeacherFavor.user_id == User.user_id)
        query = query.join(Works, Works.works_id == TeacherFavor.works_id)
        query = query.join(IndexVideo, Works.works_id == IndexVideo.works_id)
        query = query.join(Video, IndexVideo.video_id == Video.video_id)
        query = query.join(Task, TeacherFavor.task_id == Task.task_id)
        query = query.filter(TeacherFavor.created > term.currentterm)
        if user.is_teacher:
            query = query.filter(TeacherFavor.user_id == user.user_id)
        query = query.order_by(desc(TeacherFavor.created))
        query = query.limit(7)
        favors = query.all()
        return favors
        
        
        
        
        
        
        
        
        
        
        
        
        
        


class TeacherFavorLove(Base):
    __table__ = teacher_favor_love


class TeacherFavorComment(Base):
    __table__ = teacher_favor_comment
    
    @property
    def reply(self):
        return session.query(TeacherFavorComment).filter(TeacherFavorComment.id == self.reply_id).first()
    
    @property
    def user(self):
        from lib.functions import load_user
        return load_user(self.user_id)

