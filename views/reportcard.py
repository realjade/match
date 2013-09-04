# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, session, url_for, redirect, \
        render_template, abort, g, flash, json, Response, make_response, current_app,send_file
import models as m
from models.tables import User,Admin,Classgrade,Task,Video,Works,School,TeacherFavor,\
        Taskbox,ClassTask,UserClass,TimeLine,TimeLineEvent, IndexVideo,TeacherFavorComment,\
        TeacherFavorLove, FavImgCreate,FavImg, FavImgBox,FavImgUser,\
        FavImgItem,FavImgComment,FavVideoCreate,FavVideo,FavVideoUser,FavVideoBox,FavVideoItem,FavVideoComment,ReportCard
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
from datetime import datetime
from lib import const, videoworks
import os
from sqlalchemy import desc, asc

# Flask 模块对象
module = Blueprint('reportcard', __name__)

digitdict = {
             1:u'\u2460',
             2:u'\u2461',
             3:u'\u2462',
             4:u'\u2463',
             5:u'\u2464',
             6:u'\u2465',
             7:u'\u2466',
             8:u'\u2467',
             9:u'\u2468',
             0:u'\u24ea',
             }

@module.route('/reportcard/online/', methods=['GET','POST'])
@module.route('/reportcard/online/<class_id>/', methods=['GET','POST'])
@module.route('/reportcard/online/child/<child_id>/', methods=['GET','POST'])
@module.route('/reportcard/online/child/<child_id>/<class_id>/', methods=['GET','POST'])
@login_required
def reportcard_online(class_id=None,child_id=None):
    user = g.user
    if user.isparent:
        user = m.session.query(User).filter(User.user_id == child_id).first()
    #获得该用户所有的班级
    classes = user.classgrades_model()
    if not class_id and len(classes)>0:
        class_id = classes[0].class_id
    term = f.SchoolTerm()
    #得到该班级下所有的作业
    tasks = m.session.query(Task,ClassTask).filter(Task.task_type ==1,Task.created >= term.currentterm) \
                             .join(ClassTask,Task.task_id == ClassTask.task_id).filter(ClassTask.class_id == class_id).order_by(desc(Task.created)).all()
    #获得该班级所有学生
    users = m.session.query(UserClass,User).filter(UserClass.class_id == class_id,UserClass.valid == True, UserClass.identity == 0) \
                                .join(User,UserClass.user_id == User.user_id).filter(User.is_student == 1).order_by(asc(User.nickname)).all()
    taskarray = map(lambda x:x.Task.task_id,tasks)
    taskdict = dict(map(lambda x:(x.Task.task_id,x.Task),tasks))
    
    result = {}
    for uc,suser in users:
        works = m.session.query(Taskbox,Works).filter(Taskbox.user_id == suser.user_id,Taskbox.task_id.in_(taskarray)) \
                                    .outerjoin(Works,Taskbox.works_id == Works.works_id)
        worksdict = dict(map(lambda x:(x.Taskbox.task_id,x),works))
        for tid in taskdict:
            if not result.get(tid,None):
                work = worksdict.get(tid,None)
                if work and work.Works:
                    result[tid] = [int(work.Works.star)]
                else:
                    result[tid] = ['-',]
            else:
                work = worksdict.get(tid,None)
                if work and work.Works:
                    result[tid].append(int(work.Works.star))
                else:
                    result[tid] .append('-')
    today = datetime.now()
    year = today.year
    month = today.month
    period = u'二' if (month >= 9 and month <= 12) or (month>=1 and month<=2) else u'一'
    if g.user.isparent:
        return render_template('reportcard/online.html', classes = classes, results = result, tasks= taskdict,tasksarray = taskarray, students = users, curstudent = user,count = len(users),class_id = class_id,year=year,period=period, tab='child',subtab=child_id,subsubtab='online')
    else:
        return render_template('reportcard/online.html', classes = classes, results = result, tasks= taskdict,tasksarray = taskarray, students = users, curstudent = user,count = len(users),class_id = class_id,year=year,period=period, tab='reportcard',subtab='online')
        

@module.route('/reportcard/online/<class_id>/export/', methods=['GET','POST'])
@teacher_required
def reportcard_online_export(class_id=None):
    file,filename = f.teacher_task_export(g.user,class_id = class_id)
    return send_file(file,as_attachment = True,attachment_filename=filename.encode('utf8'))

@module.route('/reportcard/classroom/', methods=['GET','POST'])
@module.route('/reportcard/classroom/<class_id>/', methods=['GET','POST'])
@module.route('/reportcard/classroom/child/<child_id>/', methods=['GET','POST'])
@module.route('/reportcard/classroom/child/<child_id>/<class_id>/', methods=['GET','POST'])
@login_required
def reportcard_classroom(class_id=None,child_id = None):
    user = g.user
    error = None
    if user.isteacher:
        classgrades = g.user.classgrades
        if not class_id and len(classgrades)>0:
            class_id = classgrades[0]['class_id']
        query = m.session.query(ReportCard).filter(ReportCard.user_id == user.user_id)
        if class_id:
            query = query.filter(ReportCard.class_id == class_id)
        query = query.order_by(desc(ReportCard.created))
        reportcards = query.all()
        if request.method == 'POST':
            file = request.files.get('file')
            class_id = request.form.get('class_id',None)
            if not class_id:
                error = u'请选择一个班级'
            else:
                if not file:
                    name = request.args.get('name')
                    file = FileStorage(request.stream, filename=name, name=name, headers=request.headers)
                if file and f.allowed_excel(file.filename):
                    fh = FileHelper(file,rootdir = "static/reportcard")
                    fh.save()
                    fh.move()
                    reportcard = ReportCard()
                    reportcard.reportcard_id = ut.create_reportcard_id()
                    reportcard.user_id = g.user.user_id
                    reportcard.reportcard_path = fh.finalpath.replace(current_app.root_path, '')
                    reportcard.reportcard_name = file.filename
                    reportcard.class_id = class_id
                    reportcard.created = int(time.time()*1000)
                    m.session.add(reportcard)
                    m.session.commit()
                    return redirect('/reportcard/classroom/%s/'%class_id)
                else:
                    error = u'文件不存在或者格式不正确'
    else:
        if user.isparent:
            user = m.session.query(User).filter(User.user_id == child_id).first()
        classgrades = user.classgrades_model()
        classids = map(lambda x:x.class_id,classgrades)
        teachers = m.session.query(UserClass,User).filter(UserClass.class_id.in_(classids),UserClass.is_creator == 1) \
                            .join(User,UserClass.user_id == User.user_id).all()
        teacherids = map(lambda x:x.User.user_id,teachers)
        query = m.session.query(ReportCard,User).filter(ReportCard.user_id.in_(teacherids)) \
                        .join(User,User.user_id == ReportCard.user_id)
        if not class_id and len(classgrades)>0:
            class_id = classgrades[0].class_id
        if class_id:
            query = query.filter(ReportCard.class_id == class_id)
        query = query.order_by(desc(ReportCard.created))
        reportcards = query.all()
    if g.user.isparent:
        return render_template('reportcard/classroom.html',reportcards = reportcards,classgrades = classgrades,class_id = class_id,child_id = child_id, tab='child',subtab=child_id,subsubtab='classroom')
    else:
        return render_template('reportcard/classroom.html',reportcards = reportcards,classgrades = classgrades,class_id= class_id, error=error, tab='reportcard',subtab='classroom')
        
@module.route('/reportcard/classroom/import/', methods=['GET','POST'])
@teacher_required
def reportcard_classroom_import():
    file = request.files.get('file')
    reportcard_id = request.values.get('reportcard_id',None)
    if not file:
        name = request.args.get('name')
        file = FileStorage(request.stream, filename=name, name=name, headers=request.headers)
    if file and f.allowed_excel(file.filename):
        fh = FileHelper(file,rootdir = "static/reportcard")
        fh.save()
        fh.move()
        reportcard = m.session.query(ReportCard).filter(ReportCard.reportcard_id == reportcard_id).first()
        if reportcard:
            reportcard.reportcard_path = fh.finalpath.replace(current_app.root_path, '')
            reportcard.reportcard_name = file.filename
            m.session.commit()
        else:
            return f.failed(*const.UPLOAD_FAIL)
        if fh.savepath:
            return f.succeed({'filepath':fh.savepath})
    return f.failed(*const.UPLOAD_FAIL)
    
