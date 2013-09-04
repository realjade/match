# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
import time
from sqlalchemy import desc, asc


video = Table("video", metadata, autoload=True)
index_video = Table("index_video", metadata, autoload=True)


class Video(Base):
    __table__ = video
            
    @property
    def user(self):
        from lib.functions import load_user
        return load_user(self.user_id)
        
    def student_other_video(self):
        """当前视频学生用户的其他推荐视频"""
        from models.works import Works
        from models.task import Task, Taskbox
        from models.favor_video import TeacherFavor
        query = session.query(Works,Video,Task,TeacherFavor)
        query = query.filter(Works.user_id == self.user_id)
        query = query.join(IndexVideo, Works.works_id == IndexVideo.works_id)
        query = query.join(Video, IndexVideo.video_id == Video.video_id)
        query = query.join(TeacherFavor, TeacherFavor.works_id == Works.works_id)
        query = query.join(Task, TeacherFavor.task_id == Task.task_id)
        return query.all()


class IndexVideo(Base):
    __table__ = index_video
