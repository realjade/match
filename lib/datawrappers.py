# -*- coding: utf-8 -*-
import os
import utils as ut
from flask import json, g
import models as m
from models.tables import User, Admin, Classgrade, Task, Video, Works, School, TeacherFavor, \
        Taskbox, ClassTask, UserClass, TimeLine, TimeLineEvent
from sqlalchemy import or_
from sqlalchemy import desc, asc
from sqlalchemy.orm import aliased
import time
from datetime import datetime
import types
import lib.filters as ft
import lib.filehelper as fh
from lib.filters import format_datetime

def wrap_teacher_favor(teacher_favor, user, works, video, student, task):
    return {'teacher':user.nickname, 'time':ft.format_datetime(teacher_favor.created), 
        'click':teacher_favor.click,'love':teacher_favor.love,'reply':teacher_favor.reply,
        'student': student.nickname,'student_id':student.user_id, 'task_content': task.task_content, 
        'video_id':video.video_id, 'video_path':video.video_path, 
        'thumbnail_path':video.thumbnail_path,'works_id':teacher_favor.works_id,
        'classgrade':teacher_favor.classgrade.class_name,
        'parent_comment':works.parent_comment,'teacher_comment':works.teacher_comment,
        'star':works.star}

def wrap_videos(video, indexvideo):
    r = {'video_id':video.video_id, 'video_path':video.video_path, 'thumbnail_path':video.thumbnail_path,
        'time':ft.format_datetime(video.created), 'works_id':'', 'task_id':''}
    if indexvideo:
        r['works_id'] = indexvideo.works_id
        r['task_id'] = indexvideo.task_id
    return r

def wrap_attachments(attachments,attachmentdt=None,task_id = None):
    if attachmentdt:
        result = []
        if len(attachmentdt) == len(attachments):
            for path,filename in attachmentdt.items():
                result.append({'path':u"/fujian%s?task_id=%s" % (path,task_id),'filename':filename})
            return result
    return [{'path':u"/fujian%s" % path,'filename':os.path.basename(path)} for path in attachments]
        

def wrap_task(task,extra={}):
    if not task:
        return None
    result = {
            'task_id':task.task_id,
            'task_content':task.task_content,
            'description':task.description,
            'task_type':task.task_type,
            'isvideo':task.isvideo,
            'iswriting':task.iswriting,
            'isimage':task.isimage,
            'istext':task.istext,
            'isvalid':task.isvalid,
            'isnotify':task.isnotify,
            'task_type_text':_task_type(task),
            'classgrades':task.classgrades,
            'need_approval':task.need_approval==1,
            'updatetime':ft.format_datetime(task.updated),
            'deadline':ft.format_datetime(task.dead_line),
            'attachments':wrap_attachments(task.extra.get('attachments',[]),task.extra.get('attachmentdt',None),task.task_id)
            }
    works = extra.get('works',None)
    if not works or (works and not works.get("video",{}).get("isfinished",False)):
        result.update({'state':'newwork'})
        if not task.isvalid:
            result.update({'state':'invalid'})
    else:
        result.update({'state':'needapproval'})# 默认显示需要家长点评
        #TODO 如果是学生 没有父母 并且未提交 显示自我点评
        if False:
            result.update({'state':'need-studentapproval'})
        # 如果点评 显示等待教师点评 #TODO 重写逻辑
        if works.get('isapproval',False):
            result.update({'state':'needcorrect'})
        # 如果是重做 显示重做图标
        if works.get('isredo',False):
            result.update({'state':'redo'})
        if g.user.isteacher and works.get("teacher_comment") != u'老师没有给评语':
            # 评论内容不为None 则认为是重做
            result.update({'state':'redo-teacher'})
        # 如果是已经批改完成 不显示标签
        if works.get('isread',False):
            result.update({'state':'done'})
    if works and works.get('created',0)>task.dead_line:
        result.update({'outday':True})
    return result

def wrap_work(work,extra={}):
    if not work:
        return None
    favor = m.session.query(TeacherFavor) \
            .filter(TeacherFavor.works_id == work.works_id) \
            .first()
    return {
            'works_id':work.works_id,
            'video':work.video,
            'isapproval':work.parent_approval != 0,
            'parent_comment':work.parent_comment if work.parent_comment else u'家长没有给点评意见哟',
            'isread':work.teacher_readed == 1,
            'teacher_comment':work.teacher_comment if work.teacher_comment != None else u'老师没有给评语',
            'isfavor':work.isfavor,
            'star':int(work.star),
            'updatetime':ft.format_datetime(work.updated),
            'isredo':work.redo == 1,
            'image':work.image
            }
    
def wrap_video(video,extra={}):
    if not video:
        return None
    return {
            'user_id':video.user_id,
            'video_id':video.video_id,
            'video_path':video.video_path,
            'thumbnail_path':video.thumbnail_path,
            'updatetime':ft.format_datetime(video.updated),
            'isconvert':video.status == 'convert',
            'isfailed':video.status == 'failed',
            'isfinished':video.status == 'finished',
            }

def wrap_user(user,extra={}):
    if not user:
        return None
    return {
            'user_id':user.user_id,
            'course':user.course,
            'isstudent':user.isstudent,
            'isteacher':user.isteacher,
            'isparent':user.isparent,
            'smallavatar': ft.avatar(user),
            'mediumavatar': ft.avatar(user,'medium'),
            'bigavatar': ft.avatar(user,'big'),
            'nickname':user.nickname,
            'email':user.email,
            'mobile':user.mobile,
            }
    
def wrap_classgrade(classgrade,extra={}):
    if not classgrade:
        return None
    return {
            'class_name':classgrade.class_name,
            'class_id':classgrade.class_id,
            'email':classgrade.email,
            'description':classgrade.extra.get('description'),
            'creator':classgrade.creator,
            'created':format_datetime(classgrade.created),
            'updated':classgrade.updated,
            'school':classgrade.school,
            'description':classgrade.extra.get('description'),
            'tname':classgrade.creator.get('nickname',''),
            'class_invitation':True
            }

def wrap_school(school,extra={}):
    if not school:
        return None
    return {
            'school_id':school.school_id,
            'province':school.province,
            'city':school.city,
            'county':school.county,
            'school_name':school.school_name,
            'created':school.created,
            'updated':school.updated,
            'fullname':school.fullname
            }
def _task_type(task):
    if task.isvideo:
        return u'视频'
    if task.iswriting:
        return u'笔头'
    if task.isnotify:
        return u'通知'
    if task.isimage:
        return u'图片'
    if task.istext:
        return u'文字'
