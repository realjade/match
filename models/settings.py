# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session


feedback = Table('feedback',metadata, autoload = True)

#TODO 可以删除的表
teacher_video = Table("teacher_video",metadata,autoload=True)
teacher_video_comment = Table("teacher_video_comment",metadata,autoload=True)
timeline = Table("timeline", metadata, autoload=True)
ireadcount = Table('ireadcount', metadata, autoload = True)



class Feedback(Base,buildmixin('extra')):
    __table__ = feedback

#TODO -------------------------------------------------
class TeacherVideo(Base):#TODO delete
    __table__ = teacher_video

class TeacherVideoComment(Base):#TODO delete
    __table__ = teacher_video_comment

class TimeLine(Base, buildmixin('extra')):#TODO delete
    __table__ = timeline

class IreadCount(Base):#TODO delete
    __table__ = ireadcount

class TimeLineEvent():#TODO delete
    classcreate = 'class.create'
    classjoin = 'class.join'
    classquit = 'class.quit'
    taskpublish = 'task.publish'
    taskcomplete = 'task.complete'
    worksteachercorrect = 'works.teacher.correct'
    worksapproval = 'works.approval'
    worksparentcomment = 'works.parent.comment'
