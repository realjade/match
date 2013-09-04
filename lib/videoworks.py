# -*- coding: utf-8 -*-

import os
import utils as ut
from flask import json, g
import models as m
from models.tables import User, Admin, Classgrade, Task, Video, Works, School, TeacherFavor, \
        Taskbox, ClassTask, UserClass, TimeLine, TimeLineEvent, IndexVideo
from sqlalchemy import or_
from sqlalchemy import desc, asc
from sqlalchemy.orm import aliased
import time
from datetime import datetime
import types

def load_nottasK_videos(user_id):
    videos = m.session.query(Video).filter(Video.user_id == user_id) \
                .outerjoin(IndexVideo, IndexVideo.video_id == Video.video_id) \
                .filter(IndexVideo.id == None) \
                .order_by(desc(Video.created)) \
                .limit(20).all()

    videos = map(lambda x: {'video_path':x.video_path, 'thumbnail_path':x.thumbnail_path, 'video_id':x.video_id}, videos)
    return videos

def is_video_not_using(user_id, video_id):
    videos = m.session.query(Video).filter(Video.video_id == video_id) \
                .outerjoin(IndexVideo, IndexVideo.video_id == Video.video_id) \
                .filter(IndexVideo.id == None) \
                .limit(10).all()
    if len(videos) > 0:
        return True
    return False