# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, render_template, g, current_app
from models.tables import Task,Video,Works,Taskbox,IndexVideo
import models as m
import time
import os
import lib.functions as f
import lib.utils as ut
import lib.datawrappers as dw
from lib.videohelper import VideoHelper
from lib.filehelper import FileHelper
from lib import const, videoworks
from werkzeug.datastructures import FileStorage
from lib.wrappers import login_required, jsonify
from lib.videohelper import VideoHelper
from celerytasks import videotask
import config
from random import choice
import string


module = Blueprint('video', __name__)


@module.route('/task/upload/', methods=['POST'])
@login_required
def upload_video():
    """作业上传，视频或者图片"""
    file = request.files.get('file')
    if not file:
        name = request.args.get('name')
        file = FileStorage(request.stream, filename=name, name=name, headers=request.headers)
    task_id = request.values.get('task_id', '').strip()
    child_id = request.values.get('child_id','').strip()
    user = g.user
    if child_id and child_id !='None' and child_id not in user.extra.get('children',[]):
        return f.failed(*const.HANDIN_NOT_YOURCHILD)
    user_id = g.user.user_id
    if child_id and child_id !='None':
        user_id = child_id
    tw = m.session.query(Taskbox,Task,Works).filter(Taskbox.task_id == task_id,Taskbox.user_id == user_id) \
    .join(Task,Taskbox.task_id == Task.task_id) \
    .outerjoin(Works,Taskbox.works_id == Works.works_id).first()
    if not tw:
        return f.failed(*const.HOMEWORK_NOT_EXIST)
    else:
        if tw.Works and tw.Works.teacher_readed == 1:
            return f.failed(*const.HOMEWORK_HASCORRECT)
    if file:
        task = tw.Task
        if task.isvideo:
            if f.allowed_file(file.filename):
                #如果是视频作业
                v = Video(
                    user_id = user_id,
                    video_id = ut.create_video_id(),
                    video_path = '',
                    thumbnail_path = '',
                    status = 'convert',
                    created=int(time.time()*1000), updated=int(time.time()*1000))
                m.session.add(v)
                video_id = v.video_id
            else:
                return f.failed(*const.VIDEO_NOT_SUPPORT)
        if task.isimage:
            #如果是图片作业
            if f.allowed_img_file(file.filename):
                fh = FileHelper(file,rootdir = "static/task_img")
                fh.save()
                fh.move()
                thumbnail_path = fh.thumbnail(135,110)# 生成缩略图
                image_path = ''
                if fh.finalpath:
                    image_path = fh.finalpath.replace(current_app.root_path, '')
            else:
                return f.failed(*const.IMAGE_NOT_SUPPORT)
        #自动提交作业
        taskbox = tw.Taskbox
        if not taskbox.works_id:
            #没有交过作业
            w = Works(
                user_id = user_id,
                works_id = ut.create_works_id(),
                parent_approval = 0,
                teacher_readed = 0,
                star = 0,
                created=int(time.time()*1000), updated=int(time.time()*1000)
                )
            if task.isvideo:
                w.content.update({'isvideo':True,'video_id':video_id})
            m.session.add(w)
            taskbox.works_id = w.works_id
            taskbox.updated = int(time.time()*1000)
            if task.isvideo:
                #查看视频是否已经记录
                iv = m.session.query(IndexVideo).filter(IndexVideo.video_id == video_id, IndexVideo.works_id == w.works_id).first()
                if not iv:
                    iv = IndexVideo(
                        works_id = w.works_id,
                        video_id = video_id,
                        task_id = task_id,
                        created=int(time.time()*1000), updated=int(time.time()*1000)
                        )
                    m.session.add(iv)
        else:
            #交过作业情况
            w = tw.Works
            w.redo = 0
            w.updated = int(time.time()*1000)
            if task.isvideo:
                iv = m.session.query(IndexVideo).filter(IndexVideo.video_id == w.content.get('video_id',''), IndexVideo.works_id == w.works_id).first()
                w.content.update({'video_id':video_id})
                if iv:
                    iv.video_id = video_id
        if task.isimage:
            image_paths = w.content.get('image_path',[])
            image_thumbnail_paths = w.content.get('image_thumbnail_path',[])
            image_paths.append(image_path)
            image_thumbnail_paths.append(thumbnail_path)
            w.content.update({'isimage':True,'image_path':image_paths,'image_thumbnail_path':image_thumbnail_paths})
        m.session.commit()
        if task.isvideo:
            vh = VideoHelper(filestream = file)
            vh.save()
            vh.get_thumbnail(tmp = True)
            savepath = vh.savepath.replace(current_app.root_path, '')
            videotask.conver_video.apply_async((savepath, video_id, '0'),countdown = 60*3)
            return f.succeed({
                              'thumbnail_path':vh.thumbnail.replace(current_app.root_path, ''),
                              'savepath':savepath,
                              'video_id':video_id,
                              'child_id':child_id if child_id and child_id !=None else ''
                              })
        else:
            teacher = f.load_user(task.creator)
            data = {'works':dw.wrap_work(w)}
            data.update(student = dw.wrap_user(f.load_user(user_id)))
            if child_id and child_id !='None' and user.isparent:
                data.update(parent = dw.wrap_user(user))
            else:
                data.update(parent = dw.wrap_user(user.parent))
            data.update(user = dw.wrap_user(user))
            data.update(teacher = dw.wrap_user(teacher))
            extra = {}
            extra['works'] = data['works']
            data.update(task = dw.wrap_task(task,extra = extra))
            if task.isvideo:
                data.update(video=dw.wrap_video(v))
            return f.succeed(data)
    else:
        return f.failed(*const.VIDEO_NOT_SUPPORT)

@module.route('/task/image/remove/', methods=['POST'])
@login_required
def task_image_remove():
    path = request.form.get('path',None)
    works_id = request.form.get('works_id',None)
    child_id = request.form.get('child_id',None)
    user_id = g.user.user_id if not child_id else child_id
    works = m.session.query(Works).filter(Works.works_id == works_id,Works.user_id == user_id).first()
    if works.teacher_readed == 1:
            return f.failed(*const.HOMEWORK_HASCORRECT)
    if works.parent_approval == 1:
            return f.failed(*const.HOMEWORK_HASAPPROVAL)
    if not works:
        return f.failed(*const.INVALID_PARAMS)
    image_paths = works.content.get('image_path',[])
    image_thumbnail_paths = works.content.get('image_thumbnail_path',[])
    try:
        image_thumbnail_paths.remove(image_thumbnail_paths[image_paths.index(path)])
        image_paths.remove(path)
        works.content.update({'isimage':True,'image_path':image_paths,'image_thumbnail_path':image_thumbnail_paths})
        m.session.commit()
    except:
        return f.failed(*const.INVALID_Failed)
    return f.succeed({
                      'image_path':image_paths,
                      'thumbnail_path':image_thumbnail_paths,
                      'works_id':works_id,
                      'child_id':child_id
                      })

    
@module.route('/upload/video/transpose/', methods=['POST'])
@login_required
def upload_video_transpose():
    '''
        视频旋转
    '''
    thumbnail_path = request.form.get('thumbnail_path',None)
    savepath = request.form.get('savepath',None)
    rotate = request.form.get('rotate',None)
    video_id = request.form.get('video_id',None)
    os.remove(current_app.root_path+thumbnail_path)
    videotask.conver_video.apply_async((savepath, video_id, rotate))
    '''rootpath = config.ROOTPATH
    filename,ext = os.path.splitext(savepath)
    finalpath = '%s_%s%s'%(filename, ''.join([choice(string.digits) for i in range(4)]), '.mp4')
    vh = VideoHelper(savepath = rootpath+savepath,root_path = rootpath, rotate = rotate,finalpath = rootpath+finalpath)
    video = m.session.query(Video).filter(Video.video_id == video_id).first()
    if video:
        if vh.read_and_process():
            meta = vh.get_meta()
            video_path = vh.finalpath.replace(rootpath, '')
            thumbnail = vh.thumbnail.replace(rootpath,'')
            video.video_path = video_path
            video.thumbnail_path = thumbnail
            video.status = 'finished'
        else:
            video.status = 'failed'
        m.session.commit()'''
    return f.succeed('ok')


@module.route('/video/get/', methods=['GET', 'POST'])
@login_required
def internal_video_get():
    video_id = request.values.get('video_id',None)
    if not video_id:
        return f.failed(*const.INVALID_PARAMS)
    video = m.session.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        return f.failed(*const.VIDEO_NOT_EXIST)
    return f.succeed(dw.wrap_video(video))

@module.route('/internal/video/get/', methods=['GET', 'POST'])
def internal_video_get():
    video_id = request.values.get('video_id',None)
    if not video_id:
        return f.failed(*const.INVALID_PARAMS)
    video = m.session.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        return f.failed(*const.VIDEO_NOT_EXIST)
    return f.succeed(dw.wrap_video(video))
    
@module.route('/internal/video/update/', methods=['GET', 'POST'])
def internal_video_update():
    video_id = request.values.get('video_id',None)
    status = request.values.get('status',None)
    video_path = request.values.get('video_path',None)
    thumbnail_path = request.values.get('thumbnail_path',None)
    if not video_id or not status:
        return f.failed(*const.INVALID_PARAMS)
    video = m.session.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        return f.failed(*const.VIDEO_NOT_EXIST)
    video.status = status
    video.video_path = video_path
    video.thumbnail_path = thumbnail_path
    m.session.commit()
    return f.succeed(dw.wrap_video(video))
