# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, render_template, g, current_app, send_file
import models as m
import time
from lib.wrappers import login_required, teacher_required
import lib.functions as f
from lib import const, videoworks, mail,filters as ft
import lib.utils as ut
from models.tables import Task,MultiTask,TeacherFavor,Taskbox,ClassTask,UserClass,TimeLine,Works,Classgrade
import lib.datawrappers as dw
from lib.filehelper import FileHelper
from datetime import datetime


module = Blueprint('task_teacher', __name__)


@module.route('/task/summary/', methods=['GET', 'POST'])
@login_required
def task_summary():
    """作业统计"""
    ret = f.task_summary(g.user)
    return render_template('/task/summary.html',tab = 'tasksummary',title=u'作业统计',classes =ret)

@module.route('/task/export/', methods=['GET', 'POST'])
@module.route('/task/export/<task_id>/', methods=['GET', 'POST'])
@teacher_required
def task_export(task_id=None):
    """作业导出"""
    file,filename = f.teacher_task_export(g.user,task_id = task_id)
    return send_file(file,as_attachment = True,attachment_filename=filename.encode('utf8'))


@module.route('/task/show/<task_id>/', defaults = {'class_id':None})
@module.route('/task/show/<task_id>/<class_id>/')
@login_required
def task_show(task_id=None,class_id=None):
    """批量修改同主题 显示"""
    
    task = m.session.query(Task).filter(Task.task_id == task_id).first()
    classes = task.classgrades_model()
    if not class_id:
        class_id = classes[0].class_id
    notreadedworks,page = f.pages(f.teacher_works,g.user,task_id=task_id,class_id = class_id,filter_key = "notreaded")
    readedworks,page = f.pages(f.teacher_works,g.user,task_id=task_id,class_id = class_id,filter_key = "readed")
    return render_template('/task/teacher/task_show_title.html',
            readedworks = readedworks,notreadedworks=notreadedworks,page=page,classes = classes,task_id = task_id,class_id = class_id,
            tab = 'task',subtab = 'notreaded',task={'outday':False})

@module.route('/teacher/task/publish/',methods=['GET','POST'])
@teacher_required
def taks_publish():
    """ajax 发布作业"""
    content = request.values.get('content','')
    description = request.values.get('description','')
    needapproval = 1 #request.values.get('need_approval','true').lower() == 'true'
    tasktype = request.values.get('type','0')
    deadline = request.values.get('deadline', '')
    class_ids = request.values.get('class_ids', ',').split(',')
    filepath = request.values.getlist('filepath')
    filename = request.values.getlist('filename')
    ismulti = request.values.get('multi','0')
    sendemail = request.values.get('sendemail','0')
    if not tasktype or not content or not class_ids:
        return f.failed(*const.INVALID_PARAMS)
    class_ids = filter(lambda x: x, class_ids)
    if len(class_ids) == 0:
        return f.failed(*const.CLASSGRADE_NOT_EXIST)
    attachments = []
    attachmentdt = {}
    for fp,fn in zip(filepath,filename):
        fh = FileHelper(savepath = fp)
        fh.move()
        server_path = fh.finalpath.replace(current_app.root_path, '')
        attachments.append(server_path)
        attachmentdt[server_path] = fn
    if ismulti == '0':
        task = Task(task_id = ut.create_task_id(), task_content = content,
            need_approval = needapproval, task_type = tasktype, creator = g.user.user_id,
            created = int(time.time()*1000), updated = int(time.time()*1000))
        try:
            deadline = int(deadline)
            task.dead_line = deadline + 86399*1000
        except:
            pass
        
        task.extra['attachments']=attachments
        task.extra['attachmentdt']=attachmentdt
        
        if description:
            task.extra['description']=description
        m.session.add(task)
    
        for class_id in class_ids:
            classtask = ClassTask(class_id=class_id, task_id = task.task_id, user_id = g.user.user_id,
                created = int(time.time()*1000), updated = int(time.time()*1000))
            m.session.add(classtask)
            
    
        students = m.session.query(UserClass).filter(UserClass.identity == 0,
                                                     UserClass.valid == True,
                                                     UserClass.class_id.in_(class_ids)).all()
        for student in students:
            taskbox = Taskbox(task_id = task.task_id, user_id = student.user_id, class_id = student.class_id,confirm = 0,
                 created = int(time.time()*1000), updated = int(time.time()*1000))
            m.session.add(taskbox)
            
        m.session.commit()
        for class_id in class_ids:
            classgrade = m.session.query(Classgrade).filter(Classgrade.class_id==class_id).first()
            if sendemail == '1' and classgrade.email:
                success = mail.smtp_send_mail([classgrade.email],
                                      {'event':'classtask',
                                       'user':dw.wrap_user(g.user),
                                       'task':dw.wrap_task(task),
                                       'attachments':dw.wrap_attachments(attachments,attachmentdt,task.task_id)
                                       })
        return f.succeed({'task_id':task.task_id,'content':task.task_content,'type':task.task_type,
                      'deadline':task.dead_line,'need_approval':task.need_approval,
                      'created':task.created,'updated':task.updated,'attachments':dw.wrap_attachments(attachments,attachmentdt,task.task_id)})
    else:
        #批量作业
        multitask = MultiTask(multitask_id = ut.create_multitask_id(), task_content = content,
            class_ids = request.values.get('class_ids', ','), task_type = tasktype, user_id = g.user.user_id,
            starttime = request.values.get('start',0),endtime = request.values.get('end',0),
            rate = request.values.get('rate',0),current = 0,
            created = int(time.time()*1000), updated = int(time.time()*1000))
        multitask.extra['attachments']=attachments
        multitask.extra['attachmentdt']=attachmentdt
        m.session.add(multitask)
        m.session.commit()
        return f.succeed('ok')


@module.route('/api/task/checkclassmail/',methods=['POST'])
@teacher_required
def check_classmail():
    class_ids = request.values.get('class_ids', ',').split(',')
    for class_id in class_ids:
        classgrade = m.session.query(Classgrade).filter(Classgrade.class_id==class_id).first()
        if classgrade and not classgrade.email:
            return f.failed(*(4005,u'%s未设置班级公共邮箱' % classgrade.class_name))
    return f.succeed('ok')


@module.route('/api/task/update/',methods=['POST'])
@teacher_required
def udpate_task():
    """修改作业说明"""
    task_id = request.values.get('task_id','')
    task_desc = request.values.get('task_desc','')
    task = m.session.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        return f.failed(*const.HOMEWORK_NOT_EXIST)
    task.extra['description'] = task_desc
    m.session.add(task)
    m.session.commit()
    return f.succeed({})

@module.route("/api/task/count/bytitle/", methods=['POST'])
@teacher_required
def task_count_bytitle():
    """教师批量修改作业 查询主题下有多少未批改作业"""
    works_id = request.form.get('works_id','')
    taskbox = m.session.query(Taskbox).filter(Taskbox.works_id == works_id).first()
    if taskbox:
        query = m.session.query(Taskbox,Works).filter(Taskbox.task_id == taskbox.task_id)
        query = query.filter(Taskbox.works_id!=None)
        query = query.filter(Taskbox.works_id == Works.works_id)
        query = query.filter(Works.teacher_readed == 0)
        query = query.filter(Works.parent_approval == 1)
        workscount = query.count()
        
        task = m.session.query(Task).filter(Task.task_id == taskbox.task_id).first()
        return f.succeed({'title':task.task_content,'count':workscount})
    return f.failed(*const.HOMEWORK_NOT_EXIST)


@module.route('/correct/', methods=['POST'])
@teacher_required
def correct():
    works_ids = request.form.getlist('works_id')
    if not works_ids:
        return f.failed(*const.HANDIN_NOT_EXIST)
    allworks = m.session.query(Works).filter(Works.works_id.in_(works_ids)).all()
    for works in allworks:
        t = m.session.query(Taskbox, Task).filter(Taskbox.works_id==works.works_id) \
            .join(Task,Task.task_id == Taskbox.task_id).filter(Task.creator == g.user.user_id).first()
        if not t:
            return f.failed(*const.HANDIN_NOT_YOURS)
        if works.teacher_readed == 1:
            return f.failed(*const.HOMEWORK_HASCORRECT)
        
        star = request.form.get('star',0)
        comment = request.form.get('comment','')
        redo = int(request.form.get('redo',0))
        
        works.star = star
        works.redo = redo
        works.teacher_comment = comment
        if redo:
            works.redo = redo
            works.teacher_readed = 0
            works.parent_approval = 0
        else:
            works.teacher_readed = 1
        works.updated = int(time.time()*1000)
    m.session.commit()
    return f.succeed('ok')
