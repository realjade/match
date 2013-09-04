# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, session, url_for, redirect, \
        render_template, abort, g, flash, json, Response, make_response, current_app,send_file
import models as m
from models.tables import User,Admin,Classgrade,Task,Video,Works,School,TeacherFavor,\
        Taskbox,ClassTask,UserClass,TimeLine,TimeLineEvent, IndexVideo,TeacherFavorComment,\
        TeacherFavorLove, FavImgCreate,FavImg, FavImgBox,FavImgUser,\
        FavImgItem,FavImgComment,FavVideoCreate,FavVideo,FavVideoUser,FavVideoBox,FavVideoItem,FavVideoComment,\
        TeacherFavorImg,TeacherFavorImgLove,TeacherFavorImgComment
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
from flask.ext.sqlalchemy import Pagination
from sqlalchemy import or_
import time
import lib.utils as ut
from lib.wrappers import login_required, parent_required, teacher_required, student_required
import lib.functions as f
import lib.datawrappers as dw
from lib.filters import format_datetime
from lib.videohelper import VideoHelper
from lib.filehelper import FileHelper
import datetime
from lib import const, videoworks
import os
from sqlalchemy import desc, asc
from random import choice
import string

# Flask 模块对象
module = Blueprint('favor', __name__)


@module.route('/favor/add/', methods=['POST'])
@teacher_required
def favor_add():
    """推荐学生作业"""
    works_id = request.form.get('works_id')
    if not works_id:
        return f.failed(*const.INVALID_PARAMS)
    taskbox = m.session.query(Taskbox).filter(Taskbox.works_id == works_id).first()
    if not taskbox:
        return f.failed(*const.INVALID_PARAMS)
    
    task = m.session.query(Task).filter(Task.task_id == taskbox.task_id).first()
    if not task:
        return f.failed(*const.INVALID_PARAMS)
    
    if task.isimage:
        query = m.session.query(TeacherFavorImg)
        query = query.filter(TeacherFavorImg.user_id == g.user.user_id)
        query = query.filter(TeacherFavorImg.works_id == taskbox.works_id)
        favor = query.first()
        if not favor:
            favor = TeacherFavorImg(user_id = g.user.user_id, class_id = taskbox.class_id, 
                task_id = taskbox.task_id, works_id = taskbox.works_id, created=int(time.time()*1000))
            m.session.add(favor)
            m.session.commit()
        return f.succeed('ok')
        
    else:
        favor = m.session.query(TeacherFavor) \
                    .filter(TeacherFavor.user_id == g.user.user_id, TeacherFavor.works_id == taskbox.works_id) \
                    .first()
        if not favor:
            favor = TeacherFavor(user_id = g.user.user_id, class_id = taskbox.class_id, 
                task_id = taskbox.task_id, works_id = taskbox.works_id, created=int(time.time()*1000))
            m.session.add(favor)
            m.session.commit()
        return f.succeed('ok')


@module.route('/favor/del/', methods=['POST'])
@teacher_required
def favor_del():
    """取消推荐"""
    works_id = request.form.get('works_id')
    if not works_id:
        return f.failed(*const.INVALID_PARAMS)
    query = m.session.query(TeacherFavor).filter(TeacherFavor.user_id == g.user.user_id)
    favor = query.filter(TeacherFavor.works_id == works_id).delete()
    if not favor:
        query = m.session.query(TeacherFavorImg).filter(TeacherFavorImg.user_id == g.user.user_id)
        favor = query.filter(TeacherFavorImg.works_id == works_id).delete()
    m.session.commit()
    return f.succeed('ok')


@module.route('/favor/', methods=['GET'])
@module.route('/favor/<child_id>/', methods=['GET'])
@login_required
def favor_list(child_id=None):
    page = int(request.args.get("page","1"))# 当前页
    order = request.args.get("order",None)
    order = order if order in ['click','title'] else 'time'
    term = f.SchoolTerm()
    if child_id:
        user = m.session.query(User).filter(User.user_id == child_id).first()
        if not user:
            abort(404)
    else:
        user = g.user
    class_ids = map(lambda x:x['class_id'], user.classgrades)
    
    query = m.session.query(TeacherFavor, User, Works, Video)
    if g.user.isteacher:
        query = query.filter(TeacherFavor.user_id == g.user.user_id)
    query = query.filter(TeacherFavor.created > term.currentterm)
    query = query.filter(TeacherFavor.class_id.in_(class_ids))
    query = query.join(User, TeacherFavor.user_id == User.user_id)
    query = query.join(Works, Works.works_id == TeacherFavor.works_id)
    query = query.join(IndexVideo, Works.works_id == IndexVideo.works_id)
    query = query.join(Video, IndexVideo.video_id == Video.video_id)
    query = query.join(Task, TeacherFavor.task_id == Task.task_id)
    
    count = query.count()
    
    if order == 'time':
        query = query.order_by(desc(TeacherFavor.created))
    elif order == 'title':
        query = query.order_by(desc(Task.created))
    elif order == 'click':
        query = query.order_by(desc(TeacherFavor.click))
    
    favorlist = query.offset(page*30-30).limit(30).all()# 查询的具体数据
    pagination = Pagination(query,page,30,count,favorlist)# 每页10个
    task = m.session.query(Task).filter(Task.task_id == x[0].task_id).first()
    favors = map(lambda x: dw.wrap_teacher_favor(x[0], x[1], x[2], x[3], f.load_user(x[2].user_id), task), pagination.items)
    
    if child_id:
        return render_template('favor/favor.html', 
                                favors = favors,
                                order = order,
                                tab='child',
                                subtab=child_id,
                                subsubtab="favor",
                                pagination = pagination)
    else:
        return render_template('favor/favor.html', 
                                favors = favors,
                                order = order,
                                tab='favor',
                                subtab='index',
                                pagination = pagination)


@module.route('/favor/video/<works_id>/')
@login_required
def favor_video(works_id):
    """查看推荐视频"""
    query = m.session.query(TeacherFavor,Video,Works,Task.task_content)
    query = query.filter(TeacherFavor.works_id == works_id)
    query = query.join(Works, Works.works_id == works_id)
    query = query.join(IndexVideo, TeacherFavor.works_id == IndexVideo.works_id)
    query = query.join(Video, IndexVideo.video_id == Video.video_id)
    query = query.join(Task, TeacherFavor.task_id == Task.task_id)
    favor = query.first()
    # 喜欢人数
    querylove = m.session.query(TeacherFavorLove)
    querylove = querylove.filter(TeacherFavorLove.works_id == works_id)
    querylove = querylove.filter(TeacherFavorLove.user_id == g.user.user_id)
    islove = querylove.count()
    # 增加播放次数
    teacherfavor = m.session.query(TeacherFavor).filter(TeacherFavor.works_id == works_id).first()
    teacherfavor.click = teacherfavor.click + 1
    m.session.commit()
    
    othervideos = favor.Video.student_other_video()
    return render_template('favor/favor_video.html', favor = favor,tab='favor',subtab='index',islove = islove,othervideos = othervideos)


@module.route('/favor/video/<works_id>/comment/')
@login_required
def comment(works_id):
    """加载评论"""
    page = int(request.args.get("page","1"))# 当前页
    querycomment = m.session.query(TeacherFavorComment,User)
    querycomment = querycomment.filter(TeacherFavorComment.works_id == works_id)
    querycomment = querycomment.join(User,TeacherFavorComment.user_id == User.user_id)
    count = querycomment.count()# 分页数量
    querycomment = querycomment.order_by(desc(TeacherFavorComment.created))
    commentlist = querycomment.offset(page*10 - 10).limit(10).all()# 查询的具体数据
    pagination = Pagination(querycomment,page,10,count,commentlist)# 每页10个
    return render_template('favor/comment_list.html',page=page,pagination=pagination)


@module.route('/favor/video/<works_id>/love/', methods=["POST"], defaults= {'state':'add'})
@module.route('/favor/video/<works_id>/dellove/', methods=["POST"], defaults= {'state':'del'})
@login_required
def favor_video_love(works_id,state):
    """秀场 喜欢和取消喜欢视频"""
    works = m.session.query(Works).filter(Works.works_id == works_id).first()
    querylove = m.session.query(TeacherFavorLove)
    querylove = querylove.filter(TeacherFavorLove.works_id == works_id)
    querylove = querylove.filter(TeacherFavorLove.user_id == g.user.user_id)
    
    teacherfavor = m.session.query(TeacherFavor).filter(TeacherFavor.works_id == works_id).first()
    if state == 'add':
        islove = querylove.count()
        if works and islove == 0:
            teacherfavor.love = teacherfavor.love + 1
            favor_love = TeacherFavorLove()
            favor_love.works_id = works_id
            favor_love.user_id = g.user.user_id
            favor_love.created=int(time.time()*1000)
            m.session.add(favor_love)
            m.session.commit()
        return f.succeed('ok')
    else:
        querylove.delete()
        
        if teacherfavor:
            teacherfavor.love = teacherfavor.love - 1
        m.session.commit()
        return f.succeed('ok')
    return f.failed(*const.INVALID_PARAMS)


@module.route('/favor/video/<works_id>/sendcomment/',methods=["POST"])
@login_required
def fav_sendcomment(works_id):
    """评论秀场视频"""
    works = m.session.query(Works).filter(Works.works_id == works_id).first()
    if works:
        teacherfavor = m.session.query(TeacherFavor).filter(TeacherFavor.works_id == works_id).first()
        teacherfavor.reply = teacherfavor.reply + 1
        comment = request.form.get("comment")
        reply_id = request.form.get("reply_id")
        tfcm = TeacherFavorComment()
        tfcm.works_id = works_id
        tfcm.user_id = g.user.user_id
        tfcm.comment = comment
        tfcm.reply_id = reply_id
        tfcm.created=int(time.time()*1000)
        m.session.add(tfcm)
        m.session.commit()
        return f.succeed("ok")
    return f.failed(*const.INVALID_PARAMS)


#################################################################

@module.route('/favor/taskimg/', methods=['GET'])
@module.route('/favor/taskimg/<child_id>/', methods=['GET'])
@login_required
def favortaskimg(child_id = None):
    page = int(request.args.get("page","1"))# 当前页
    order = request.args.get("order",None)
    order = order if order in ['click','title'] else 'time'
    term = f.SchoolTerm()
    if child_id:
        user = m.session.query(User).filter(User.user_id == child_id).first()
        if not user:
            abort(404)
    else:
        user = g.user
    class_ids = map(lambda x:x['class_id'], user.classgrades)
    
    query = m.session.query(TeacherFavorImg, User, Works,Task)
    if g.user.isteacher:
        query = query.filter(TeacherFavorImg.user_id == g.user.user_id)
    query = query.filter(TeacherFavorImg.created > term.currentterm)
    query = query.filter(TeacherFavorImg.class_id.in_(class_ids))
    query = query.join(User, TeacherFavorImg.user_id == User.user_id)
    query = query.join(Works, Works.works_id == TeacherFavorImg.works_id)
    query = query.join(Task, TeacherFavorImg.task_id == Task.task_id)
    
    count = query.count()
    
    if order == 'time':
        query = query.order_by(desc(TeacherFavorImg.created))
    elif order == 'title':
        query = query.order_by(desc(Task.created))
    elif order == 'click':
        query = query.order_by(desc(TeacherFavorImg.click))
    
    favorlist = query.offset(page*30-30).limit(30).all()# 查询的具体数据
    pagination = Pagination(query,page,30,count,favorlist)# 每页10个
    
    if child_id:
        return render_template('favor/favor_taskimg.html',
                                tab='child',
                                subtab=child_id,
                                subsubtab="favor",
                                order = order,
                                pagination = pagination)
    else:
        return render_template('favor/favor_taskimg.html',
                                tab='favor',
                                subtab='index',
                                order = order,
                                pagination = pagination)


@module.route('/favor/taskimg/<works_id>/show/')
@login_required
def favortaskimgshow(works_id):
    query = m.session.query(TeacherFavorImg,Works,Task.task_content)
    query = query.filter(TeacherFavorImg.works_id == works_id)
    query = query.join(Works, TeacherFavorImg.works_id == Works.works_id)
    query = query.join(Task, TeacherFavorImg.task_id == Task.task_id)
    favor = query.first()
    # 喜欢人数
    querylove = m.session.query(TeacherFavorImgLove)
    querylove = querylove.filter(TeacherFavorImgLove.works_id == works_id)
    querylove = querylove.filter(TeacherFavorImgLove.user_id == g.user.user_id)
    islove = querylove.count()
    # 增加播放次数
    teacherfavor = m.session.query(TeacherFavorImg).filter(TeacherFavorImg.works_id == works_id).first()
    teacherfavor.click = teacherfavor.click + 1
    m.session.commit()
    return render_template('favor/favor_taskimg_show.html', favor = favor,tab='favor',subtab='index',islove = islove)


@module.route('/favor/taskimg/<works_id>/show/sendcomment/',methods=["POST"])
@login_required
def favortaskimg_sendcomment(works_id):
    """评论推荐图片错误"""
    favimg = m.session.query(TeacherFavorImg).filter(TeacherFavorImg.works_id == works_id).first()
    if favimg:
        favimg.reply = favimg.reply + 1
        comment = request.form.get("comment")
        reply_id = request.form.get("reply_id")
        ficm = TeacherFavorImgComment()
        ficm.works_id = works_id
        ficm.user_id = g.user.user_id
        ficm.comment = comment
        ficm.reply_id = reply_id
        ficm.created=int(time.time()*1000)
        m.session.add(ficm)
        m.session.commit()
        return f.succeed("ok")
    return f.failed(*const.INVALID_PARAMS)


@module.route('/favor/taskimg/<works_id>/show/comment/')
@login_required
def favortaskimg_comment(works_id):
    """评论图片作业"""
    page = int(request.args.get("page","1"))# 当前页
    querycomment = m.session.query(TeacherFavorImgComment,User)
    querycomment = querycomment.filter(TeacherFavorImgComment.works_id == works_id)
    querycomment = querycomment.join(User,TeacherFavorImgComment.user_id == User.user_id)
    count = querycomment.count()# 分页数量
    querycomment = querycomment.order_by(desc(TeacherFavorImgComment.created))
    commentlist = querycomment.offset(page*10 - 10).limit(10).all()# 查询的具体数据
    pagination = Pagination(querycomment,page,10,count,commentlist)# 每页10个
    return render_template('favor/comment_list.html',page=page,pagination=pagination)


@module.route('/favor/taskimg/<works_id>/love/', methods=["POST"], defaults= {'state':'add'})
@module.route('/favor/taskimg/<works_id>/dellove/', methods=["POST"], defaults= {'state':'del'})
@login_required
def favor_taskimg_love(works_id,state):
    """秀场 喜欢和取消喜欢视频"""
    works = m.session.query(Works).filter(Works.works_id == works_id).first()
    querylove = m.session.query(TeacherFavorImgLove)
    querylove = querylove.filter(TeacherFavorImgLove.works_id == works_id)
    querylove = querylove.filter(TeacherFavorImgLove.user_id == g.user.user_id)
    
    teacherfavorimg = m.session.query(TeacherFavorImg).filter(TeacherFavorImg.works_id == works_id).first()
    if state == 'add':
        islove = querylove.count()
        if works and islove == 0:
            teacherfavorimg.love = teacherfavorimg.love + 1
            favor_love = TeacherFavorImgLove()
            favor_love.works_id = works_id
            favor_love.user_id = g.user.user_id
            favor_love.created=int(time.time()*1000)
            m.session.add(favor_love)
            m.session.commit()
        return f.succeed('ok')
    else:
        querylove.delete()
        
        if teacherfavorimg:
            teacherfavorimg.love = teacherfavorimg.love - 1
        m.session.commit()
        return f.succeed('ok')
    return f.failed(*const.INVALID_PARAMS)

#################################################################


@module.route('/favor/img/')
@login_required
def img():
    imglist = None
    if g.user.isteacher:
        imglist = m.session.query(FavImgCreate).filter(FavImgCreate.user_id == g.user.user_id).all()
    else:
        return redirect("/favor/student/img/")
    return render_template('favor/img.html',tab='favor',subtab='img',imglist=imglist)


@module.route('/favor/student/img/')
@module.route('/favor/student/img/<child_id>/')
@login_required
def student_img(child_id=None):
    if child_id:
        return render_template('favor/student/img.html',tab='child',subtab=child_id,subsubtab='img')
    return render_template('favor/student/img.html',tab='favor',subtab='img')


@module.route("/favor/img/item/")
@module.route("/favor/img/item/<child_id>/")
@login_required
def img_item(child_id=None):
    """秀场 相册列表ajax加载"""
    page = int(request.args.get("page","1"))# 当前页
    
    if child_id:
        user = m.session.query(User).filter(User.user_id == child_id).first()
    else:
        user = g.user
    class_ids = map(lambda x:x['class_id'], user.classgrades)
    
    query = m.session.query(FavImg)
    query = query.outerjoin(FavImgBox, FavImg.favimg_id == FavImgBox.favimg_id)
    query = query.filter(FavImgBox.class_id.in_(class_ids))
    query = query.group_by(FavImg.favimg_id)
    count = query.count()# 分页数量
    favimglist = query.order_by(desc(FavImg.created)).offset(page*5 - 5).limit(5).all()
    pagination = Pagination(query,page,5,count,favimglist)# 每页10个
    return render_template('favor/img_item.html',page = page,pagination=pagination)


@module.route('/favor/img/<favimg_id>/show/')
@login_required
def img_item_show(favimg_id):
    """秀场 查看单个相册"""
    favimg = m.session.query(FavImg).filter(FavImg.favimg_id == favimg_id).first()
    itemlist = m.session.query(FavImgItem).filter(FavImgItem.favimg_id == favimg_id).all()
    query = m.session.query(FavImgUser)
    query = query.filter(FavImgUser.favimg_id == favimg_id)
    user = g.user
    if user.isparent:
        query = query.filter(FavImgUser.is_read == 0)
        favimguserlist = query.filter(FavImgUser.user_id.in_([user.user_id for user in user.children])).all()
        for favimguser in favimguserlist:
            favimguser.is_read = 1
        m.session.commit()
    else:
        favimguser = query.filter(FavImgUser.user_id == user.user_id).first()
        if favimguser:
            favimguser.is_read = 1
            m.session.commit()
    return render_template('favor/img_show.html',tab='favor',subtab='img',favimg=favimg,itemlist=itemlist)



@module.route('/favor/img/<favimg_id>/show/sendcomment/',methods=["POST"])
@login_required
def fav_img_sendcomment(favimg_id):
    """评论秀场图片相册"""
    favimg = m.session.query(FavImg).filter(FavImg.favimg_id == favimg_id).first()
    if favimg:
        favimg.reply = favimg.reply + 1
        comment = request.form.get("comment")
        reply_id = request.form.get("reply_id")
        ficm = FavImgComment()
        ficm.favimg_id = favimg_id
        ficm.user_id = g.user.user_id
        ficm.comment = comment
        ficm.reply_id = reply_id
        ficm.created=int(time.time()*1000)
        m.session.add(ficm)
        m.session.commit()
        return f.succeed("ok")
    return f.failed(*const.INVALID_PARAMS)


@module.route('/favor/img/<favimg_id>/show/comment/')
@login_required
def img_comment(favimg_id):
    """秀场 评论相册"""
    page = int(request.args.get("page","1"))# 当前页
    querycomment = m.session.query(FavImgComment,User)
    querycomment = querycomment.filter(FavImgComment.favimg_id == favimg_id)
    querycomment = querycomment.join(User,FavImgComment.user_id == User.user_id)
    count = querycomment.count()# 分页数量
    querycomment = querycomment.order_by(desc(FavImgComment.created))
    commentlist = querycomment.offset(page*10 - 10).limit(10).all()# 查询的具体数据
    pagination = Pagination(querycomment,page,10,count,commentlist)# 每页10个
    return render_template('favor/comment_list.html',page=page,pagination=pagination)
    

@module.route('/favor/img/upload/', methods=['POST'])
@teacher_required
def img_upload():
    """秀场 图片上传"""
    file = request.files.get('file')
    
    if file and f.allowed_img_file(file.filename):
        fh = FileHelper(file,rootdir = "static/fav_img")
        fh.save()
        fh.move()
        thumbnail_path = fh.thumbnail()# 生成缩略图
        if fh.finalpath:
            path = fh.finalpath.replace(current_app.root_path, '')
            fic = FavImgCreate()
            fic.user_id = g.user.user_id
            fic.path = path
            fic.name = os.path.splitext(file.filename)[0]
            fic.created = int(time.time()*1000)
            fic.extra["thumbnail_path"] = thumbnail_path
            m.session.add(fic)
            m.session.commit()
            return f.succeed({'path':thumbnail_path,'id':fic.id})
    return f.failed(*const.UPLOAD_FAIL)

@module.route('/favor/img/upload/delete/', methods=['POST'])
@teacher_required
def img_delete():
    """秀场 删除图片"""
    ficid = request.form.get('ficid',None)
    fic = m.session.query(FavImgCreate).filter(FavImgCreate.id == ficid).first()
    if fic:
        m.session.query(FavImgCreate).filter(FavImgCreate.id == ficid).delete()
        joinpath = os.path.join(current_app.root_path, fic.path.replace('/','',1))
        if os.path.isfile(joinpath):
            os.remove(joinpath)
        thumbnail_path = fic.extra.get("thumbnail_path",None)
        if thumbnail_path:
            joinpath2 = os.path.join(current_app.root_path, thumbnail_path.replace('/','',1))
            if os.path.isfile(joinpath2):
                os.remove(joinpath2)
        m.session.commit()
    return f.succeed('ok')


@module.route('/favor/img/publish/', methods=['POST'])
@teacher_required
def publish_img():
    """秀场 发布相册"""
    name = request.form.get("name",None)
    reason = request.form.get("reason","")
    classids = request.form.get("classids")
    # 验证班级存在
    classlist = []
    for class_id in classids.split(","):
        classgrade = m.session.query(Classgrade).filter(Classgrade.class_id == class_id).first()
        classlist.append(classgrade)
    
    if not classlist:
        return f.failed(*const.INVALID_PARAMS)
    
    favimg = FavImg()
    favimg.favimg_id = ut.create_favimg_id()
    favimg.name = name if name else str(datetime.date.today())
    favimg.reason = reason
    favimg.user_id = g.user.user_id
    favimg.created = int(time.time()*1000)
    m.session.add(favimg)
    # 存储班级关系
    for classgrade in classlist:
        favimgbox = FavImgBox()
        favimgbox.favimg_id = favimg.favimg_id
        favimgbox.class_id = classgrade.class_id
        favimgbox.created = int(time.time()*1000)
        m.session.add(favimgbox)
        # 存储学生是否看过的关系
        for student in classgrade.newstudents:
            favimguser = FavImgUser()
            favimguser.favimg_id = favimg.favimg_id
            favimguser.user_id = student.user_id
            favimguser.class_id = classgrade.class_id
            favimguser.created = int(time.time()*1000)
            m.session.add(favimguser)
        
    
    imglist = m.session.query(FavImgCreate).filter(FavImgCreate.user_id == g.user.user_id).all()
    if len(imglist) == 0:# 如果没有图片
        return f.failed(*const.INVALID_PARAMS)
    # 图片到处 FavImgItem表
    for img in imglist:
        favimgitem = FavImgItem()
        favimgitem.favimg_id = favimg.favimg_id
        favimgitem.user_id = img.user_id
        favimgitem.name = img.name
        favimgitem.path = img.path
        favimgitem.created = img.created
        thumbnail_path  = img.extra.get("thumbnail_path",None)
        if thumbnail_path:
            favimgitem.extra["thumbnail_path"] = thumbnail_path
        m.session.add(favimgitem)
    m.session.query(FavImgCreate).filter(FavImgCreate.user_id == g.user.user_id).delete()
    m.session.commit()
    return f.succeed('ok')



##################################################################

@module.route('/favor/goodvideo/')
@login_required
def goodvideo():
    if g.user.isteacher:
        fvc = m.session.query(FavVideoCreate).filter(FavVideoCreate.user_id == g.user.user_id).first()
    else:
        return redirect("/favor/student/goodvideo/")
    return render_template('favor/goodvideo.html',tab='favor',subtab='goodvideo',fvc=fvc)


@module.route('/favor/student/goodvideo/')
@module.route('/favor/student/goodvideo/<child_id>/')
@login_required
def student_goodvideo(child_id=None):
    if child_id:
        return render_template('favor/student/video.html',tab='child',subtab=child_id,subsubtab = 'goodvideo')
    return render_template('favor/student/video.html',tab='favor',subtab='goodvideo')


@module.route('/favor/goodvideo/upload/',methods=["POST"])
@teacher_required
def goodvideo_upload():
    file = request.files.get('file')
    if file and f.allowed_file(file.filename):
        vh = VideoHelper(file)
        meta = vh.get_meta()
        v = Video(
            user_id = g.user.user_id,
            video_id = ut.create_video_id(),
            video_path = '',
            thumbnail_path = '',
            created=int(time.time()*1000), updated=int(time.time()*1000))
        m.session.add(v)
        # 存储视频
        fvc = m.session.query(FavVideoCreate).filter(FavVideoCreate.user_id == g.user.user_id).first()
        if fvc:
            fvc.name = vh.rawfname
            fvc.video_id = v.video_id
            fvc.created=int(time.time()*1000)
            fvc.thumbnail = ''
        else:
            fvc = FavVideoCreate()
            fvc.name = vh.rawfname
            fvc.video_id = v.video_id
            fvc.user_id = g.user.user_id
            fvc.thumbnail = ''
            fvc.created=int(time.time()*1000)
            m.session.add(fvc)
        m.session.commit()
        vh.save()
        vh.get_thumbnail(tmp = True)
        return f.succeed({
                          'thumbnail_path':vh.thumbnail.replace(current_app.root_path, ''),
                          'savepath':vh.savepath.replace(current_app.root_path, ''),
                          'video_id':v.video_id,
                          'fvcid':fvc.id
                          })
        
@module.route('/fav/goodvideo/transpose/', methods=['POST'])
@login_required
def upload_video_transpose():
    '''
        视频旋转
    '''
    thumbnail_path = request.form.get('thumbnail_path',None)
    savepath = request.form.get('savepath',None)
    rotate = request.form.get('rotate',None)
    video_id = request.form.get('video_id',None)
    fvcid = request.form.get('fvcid',None)
    os.remove(current_app.root_path+thumbnail_path)
    rootpath = current_app.root_path
    filename,ext = os.path.splitext(savepath)
    finalpath = '%s_%s%s'%(filename, ''.join([choice(string.digits) for i in range(4)]), '.mp4')
    vh = VideoHelper(savepath = rootpath+savepath,root_path = rootpath, rotate = rotate,finalpath = rootpath+finalpath)
    video = m.session.query(Video).filter(Video.video_id == video_id).first()
    fvc = m.session.query(FavVideoCreate).filter(FavVideoCreate.id == fvcid).first()
    if video and fvc:
        if vh.read_and_process():
            meta = vh.get_meta()
            video_path = vh.finalpath.replace(rootpath, '')
            thumbnail = vh.thumbnail.replace(rootpath,'')
            video.video_path = video_path
            video.thumbnail_path = thumbnail
            fvc.thumbnail = thumbnail
        m.session.commit()
    return f.succeed('ok')

@module.route('/favor/goodvideo/upload/delete/',methods=["POST"])
@teacher_required
def goodvideo_delete():
    fvcid = request.form.get('fvcid',None)
    fvc = m.session.query(FavVideoCreate).filter(FavVideoCreate.id == fvcid).first()
    if fvc:
        m.session.query(FavVideoCreate).filter(FavVideoCreate.id == fvcid).delete()
        video = m.session.query(Video).filter(Video.video_id == fvc.video_id).first()
        if video:
            m.session.query(Video).filter(Video.video_id == fvc.video_id).delete()
        m.session.commit()
    return f.succeed('ok')


@module.route('/favor/goodvideo/publish/',methods=["POST"])
@teacher_required
def goodvideo_publish():
    name = request.form.get("name",None)
    reason = request.form.get("reason","")
    classids = request.form.get("classids")
    # 验证班级存在
    classlist = []
    for class_id in classids.split(","):
        classgrade = m.session.query(Classgrade).filter(Classgrade.class_id == class_id).first()
        classlist.append(classgrade)
    
    if not classlist:
        return f.failed(*const.INVALID_PARAMS)
    
    fv = FavVideo()
    fv.favvideo_id = ut.create_favimg_id()
    fv.name = name
    fv.reason = reason
    fv.user_id = g.user.user_id
    fv.created = int(time.time()*1000)
    m.session.add(fv)
    for classgrade in classlist:
        fvbox = FavVideoBox()
        fvbox.favvideo_id = fv.favvideo_id
        fvbox.class_id = classgrade.class_id
        fvbox.created = int(time.time()*1000)
        m.session.add(fvbox)
        for student in classgrade.newstudents:
            fvuser = FavVideoUser()
            fvuser.favvideo_id = fv.favvideo_id
            fvuser.user_id = student.user_id
            fvuser.class_id = classgrade.class_id
            fvuser.created = int(time.time()*1000)
            m.session.add(fvuser)
    
    fvc = m.session.query(FavVideoCreate).filter(FavVideoCreate.user_id == g.user.user_id).first()
    if not fvc:
        return f.failed(*const.INVALID_PARAMS)
    
    fvi = FavVideoItem()
    fvi.favvideo_id = fv.favvideo_id
    fvi.user_id = fvc.user_id
    fvi.name = fvc.name
    fvi.video_id = fvc.video_id
    fvi.thumbnail = fvc.thumbnail
    fvi.created = fvc.created
    m.session.add(fvi)
    m.session.query(FavVideoCreate).filter(FavVideoCreate.user_id == g.user.user_id).delete()
    m.session.commit()
    return f.succeed("ok")


@module.route('/favor/goodvideo/item/')
@module.route('/favor/goodvideo/item/<child_id>/')
@login_required
def goodvideo_item(child_id=None):
    page = int(request.args.get("page","1"))# 当前页
    if child_id:
        user = m.session.query(User).filter(User.user_id == child_id).first()
    else:
        user = g.user
    class_ids = map(lambda x:x['class_id'], user.classgrades)
    
    query = m.session.query(FavVideo)
    query = query.outerjoin(FavVideoBox, FavVideo.favvideo_id == FavVideoBox.favvideo_id)
    query = query.filter(FavVideoBox.class_id.in_(class_ids))
    query = query.group_by(FavVideo.favvideo_id)
    count = query.count()# 分页数量
    favvideolist = query.order_by(desc(FavVideo.created)).offset(page*5 - 5).limit(5).all()
    pagination = Pagination(query,page,5,count,favvideolist)# 每页10个
    return render_template('favor/goodvideo_item.html',page = page,pagination=pagination)


@module.route('/favor/goodvideo/<favvideo_id>/show/')
@login_required
def goodvideo_show(favvideo_id):
    favvideo = m.session.query(FavVideo).filter(FavVideo.favvideo_id == favvideo_id).first()
    itemlist = m.session.query(FavVideoItem).filter(FavVideoItem.favvideo_id == favvideo_id).all()
    query = m.session.query(FavVideoUser)
    query = query.filter(FavVideoUser.favvideo_id == favvideo_id)
    user = g.user
    if user.isparent:
        query = query.filter(FavVideoUser.is_read == 0)
        favvideouserlist = query.filter(FavVideoUser.user_id.in_([user.user_id for user in user.children])).all()
        for favvideouser in favvideouserlist:
            favvideouser.is_read = 1
        m.session.commit()
    else:
        favvideouser = query.filter(FavVideoUser.user_id == user.user_id).first()
        if favvideouser:
            favvideouser.is_read = 1
            m.session.commit()
    return render_template('favor/goodvideo_show.html',tab='favor',subtab='goodvideo',favvideo=favvideo,itemlist=itemlist)


@module.route('/favor/goodvideo/<favvideo_id>/show/sendcomment/',methods=["POST"])
@login_required
def fav_goodvideo_sendcomment(favvideo_id):
    """评论秀场视频"""
    favvideo = m.session.query(FavVideo).filter(FavVideo.favvideo_id == favvideo_id).first()
    if favvideo:
        favvideo.reply = favvideo.reply + 1
        comment = request.form.get("comment")
        reply_id = request.form.get("reply_id")
        ficm = FavVideoComment()
        ficm.favvideo_id = favvideo_id
        ficm.user_id = g.user.user_id
        ficm.comment = comment
        ficm.reply_id = reply_id
        ficm.created=int(time.time()*1000)
        m.session.add(ficm)
        m.session.commit()
        return f.succeed("ok")
    return f.failed(*const.INVALID_PARAMS)


@module.route('/favor/goodvideo/<favvideo_id>/show/comment/')
@login_required
def goodvideo_comment(favvideo_id):
    """秀场 评论相册"""
    page = int(request.args.get("page","1"))# 当前页
    querycomment = m.session.query(FavVideoComment,User)
    querycomment = querycomment.filter(FavVideoComment.favvideo_id == favvideo_id)
    querycomment = querycomment.join(User,FavVideoComment.user_id == User.user_id)
    count = querycomment.count()# 分页数量
    querycomment = querycomment.order_by(desc(FavVideoComment.created))
    commentlist = querycomment.offset(page*10 - 10).limit(10).all()# 查询的具体数据
    pagination = Pagination(querycomment,page,10,count,commentlist)# 每页10个
    return render_template('favor/comment_list.html',page=page,pagination=pagination)
