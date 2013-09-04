# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, session, url_for, redirect, \
        render_template, abort, g, flash, json, Response, make_response, current_app
import models as m
from models.tables import User,Admin,Classgrade,Task,Video,Works,School,TeacherFavor,\
        Taskbox,ClassTask,UserClass,TimeLine,IndexVideo,Feedback,IreadCount,Notice, UserNotice
from lib.wrappers import admin_required
from datetime import datetime
from datetime import date
import time
import lib.datetimehelper as dth
import lib.utils as ut
from lib import functions as f
from sqlalchemy import desc, asc, or_

module = Blueprint('admin', __name__)

PER_PAGE = 50

@module.route('/admin/',methods=['GET'])
@admin_required
def admin():
    studentcount = _get_student_count()
    teachercount = _get_teacher_count()
    parentcount = _get_parent_count()
    classcount = _get_classgrade_count()
    schoolcount = _get_school_count()
    videocount = _get_video_count()
    return render_template('admin/admin_summary.html',studentcount = studentcount,videocount = videocount,
                           teachercount = teachercount,parentcount = parentcount,
                           classcount = classcount,schoolcount = schoolcount, tab = 'summary')

@module.route('/admin/users/',methods=['GET'])
@admin_required
def admin_users():
    page_id = request.args.get('page', '1')
    page_id = int(page_id)
    users = list_users((page_id-1)*PER_PAGE, PER_PAGE)
    users_count = m.session.query(User).count()
    pagination = ut.Pagination(page_id, PER_PAGE, users_count)
    return render_template('admin/admin_users.html', users = users, 
        pagination = pagination, tab = 'users')


@module.route('/admin/user/search/',methods=['GET', 'POST'])
@admin_required
def admin_user_search():
    users = []
    if request.method == 'POST':
        key = request.form.get('searchkey')
        if key:
            key = u'%s%s%s'%('%', key, '%')
            users = m.session.query(User).filter(or_(User.email.like(key), User.mobile.like(key), User.nickname.like(key))).all()
            users = map(lambda x: user_wrapper(x), users)
    return render_template('admin/admin_users.html', users = users, 
        pagination = None, tab = 'users')


@module.route('/admin/users/notinclass/',methods=['GET'])
@admin_required
def admin_users_notinclass():
    users = list_students_notinclass()
    return render_template('admin/admin_users.html', users = users, 
        pagination = None, tab = 'users')


@module.route('/admin/users/unusual/',methods=['GET'])
@admin_required
def admin_users_unusual():
    page_id = request.args.get('page', '1')
    page_id = int(page_id)
    users = list_unusual_users()
    #pagination = ut.Pagination(page_id, 50, len(users))
    return render_template('admin/admin_users.html', users = users, 
        pagination = None, tab = 'users')


@module.route('/admin/user/<user_id>/')
@admin_required
def user_summary(user_id):
    u = m.session.query(User).filter(User.user_id == user_id).first()
    if not u: return
    if u.isstudent:
        tasks = m.session.query(Taskbox).filter(Taskbox.user_id == u.user_id).all()
        #videos = m.session.query(Video).filter(Video.user_id == u.user_id).all()
        tworks = m.session.query(Taskbox, Task, Classgrade, Works, Video, IndexVideo).filter(Taskbox.user_id == user_id) \
            .join(Task, Taskbox.task_id == Task.task_id ) \
            .join(Classgrade, Taskbox.class_id == Classgrade.class_id ) \
            .join(Works, Taskbox.works_id == Works.works_id ) \
            .join(IndexVideo,IndexVideo.works_id == Works.works_id) \
            .join(Video, Video.video_id == IndexVideo.video_id).all()
        works = map(lambda x:{'task_content': x.Task.task_content, 'class_name':x.Classgrade.class_name,
                              'created':x.Works.created,'thumbnail_path':x.Video.thumbnail_path if x.Video else '',
                              'video_path':x.Video.video_path if x.Video else '','video_id':x.Video.video_id if x.Video else ''}, tworks)
        return render_template('admin/admin_user_summary.html', tasks = tasks,  works = works, user = user_wrapper(u), tab = 'users')
    elif u.isparent:
        return render_template('admin/admin_user_summary.html', user = user_wrapper(u), tab = 'users')
    elif u.isteacher:
        tasks = m.session.query(Task).filter(Task.creator == u.user_id).all()
        return render_template('admin/admin_user_summary.html', tasks = tasks, user = user_wrapper(u), tab = 'users')
    return ''


@module.route('/admin/user/<user_id>/delete/', methods=['POST'])
@admin_required
def delete_user(user_id):
    u = m.session.query(User).filter(User.user_id == user_id).first()
    return u'目前功能还没有实现。'
    if not u: return ''
    if u.isstudent:
        parent = u.parent
        if parent:
            children = d.extra.get('children', [])
            if u.user_id in children:
                children.pop(children.index(u.user_id))
                parent.extra.update(children = children)
        m.session.query(UserClass).filter(UserClass.user_id == u.user_id).delete()
        m.session.query(Taskbox).filter(Taskbox.user_id == u.user_id).delete()
        m.session.query(TimeLine).filter(or_(TimeLine.user_id == u.user_id, TimeLine.to_user_id == u.user_id)).delete()
        m.session.delete(u)
        m.session.commit()
    elif u.isparent:
        children = u.children
        for child in children:
            child.extra.pop('parent')
        m.session.query(TimeLine).filter(or_(TimeLine.user_id == u.user_id, TimeLine.to_user_id == u.user_id)).delete()
        m.session.delete(u)
        m.session.commit()
    elif u.isteacher:
        m.session.query(UserClass).filter(UserClass.user_id == u.user_id).delete()
        m.session.delete(u)
        m.session.commit()


@module.route('/admin/classes/',methods=['GET'])
@admin_required
def admin_classes():
    page_id = request.args.get('page','1')
    page_id = int(page_id)
    classes = list_classes()
    pagination = ut.Pagination(page_id, PER_PAGE, len(classes))
    return render_template('admin/admin_classes.html', classes = classes[(page_id-1)*PER_PAGE:page_id*PER_PAGE], 
        pagination = pagination, tab = 'classes')
    
@module.route('/admin/tasks/',methods=['GET'])
@admin_required
def admin_tasks():
    page_id = request.args.get('page','1')
    page_id = int(page_id)
    tasks = list_tasks()
    pagination = ut.Pagination(page_id, PER_PAGE, len(tasks))
    return render_template('admin/admin_tasks.html', tasks = tasks[(page_id-1)*PER_PAGE:page_id*PER_PAGE], 
        pagination = pagination, tab = 'tasks')

@module.route('/admin/task/<task_id>/<class_id>/',methods=['GET'])
@admin_required
def admin_task_summary(task_id, class_id):
    task = m.session.query(Task).filter(Task.task_id == task_id).one()
    classgrade = m.session.query(Classgrade).filter(Classgrade.class_id == class_id).one()
    tworks = m.session.query(Taskbox, User, Works, Video, IndexVideo).filter(Taskbox.task_id == task_id, Taskbox.class_id == class_id) \
            .join(Works, Taskbox.works_id == Works.works_id ) \
            .join(User, User.user_id == Taskbox.user_id)\
            .join(IndexVideo,IndexVideo.works_id == Works.works_id) \
            .join(Video,Video.video_id == IndexVideo.video_id).all()
    works = map(lambda x:{'username':x.User.nickname,'email':x.User.email, 
                          'created':x.Works.created,'thumbnail_path':x.Video.thumbnail_path if x.Video else '',
                          'video_path':x.Video.video_path if x.Video else '','video_id':x.Video.video_id if x.Video else ''}, tworks)
    return render_template('admin/admin_task_summary.html', task=task, classgrade=classgrade, works = works, tab = 'tasks')

@module.route('/admin/works/',methods=['GET'])
@admin_required
def admin_works():
    page_id = request.args.get('page','1')
    page_id = int(page_id)
    works = list_videoworks()
    pagination = ut.Pagination(page_id, PER_PAGE, len(works))
    return render_template('admin/admin_works.html', works = works[(page_id-1)*PER_PAGE:page_id*PER_PAGE], 
        pagination = pagination, tab = 'works')





@module.route('/admin/freegate/',methods=['GET', 'POST'])
@admin_required
def admin_freegate():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        user = User.get_user(username)
        if user is None:
            error = u'邮箱或者手机号不正确'
        else:
            session['user_id'] = user.user_id
            return redirect(url_for('home.home'))
    return render_template('admin/admin_freegate.html', tab = 'freegate', error = error)

                               
@module.route('/admin/feedbacks/',methods=['GET'])
@admin_required
def admin_feedbacks():
    page_id = request.args.get('page','1')
    page_id = int(page_id)
    feedbacks = list_feedbacks()
    pagination = ut.Pagination(page_id,PER_PAGE,len(feedbacks))
    return render_template('admin/admin_feedback.html',feedbacks=feedbacks[(page_id-1)*PER_PAGE:page_id*PER_PAGE],
        pagination=pagination,tab='feedback')


@module.route('/admin/ireadcount/')
def ireadcount():
    click = m.session.query(IreadCount).count()
    people = m.session.query(IreadCount).group_by(IreadCount.user_id).count()
    
    
    query = m.session.query(IreadCount,User.nickname)
    query = query.outerjoin(User,IreadCount.user_id == User.user_id)
    ireadcountli = query.order_by(IreadCount.created.desc()).all()
    page_id = request.args.get('page','1')
    page_id = int(page_id)
    pagination = ut.Pagination(page_id,PER_PAGE,len(ireadcountli))
    
    return render_template('admin/ireadcount.html',
                click=click,people=people,
                ireadcountli = ireadcountli[(page_id-1)*PER_PAGE:page_id*PER_PAGE],
                pagination = pagination)


@module.route('/admin/system/notice/', methods=["GET","POST"])
@admin_required
def system_notice():
    """发布系统通知"""
    if request.method == "GET":
        noticelist = m.session.query(Notice).order_by(Notice.created.desc()).all()
        return render_template("admin/notice.html", noticelist = noticelist)
    
    if request.method == "POST":
        userlist  = m.session.query(User).all()
        content = request.form.get("content")
        notice = Notice()
        notice_id = ut.create_notice_id()
        notice.notice_id = notice_id
        notice.content = content
        notice.creator = g.user.user_id
        notice.created = int(time.time())*1000
        m.session.add(notice)
        
        for user in userlist:
            usernotice = UserNotice()
            usernotice.accept_user  = user.user_id
            usernotice.notice_id = notice_id
            usernotice.created = int(time.time())*1000
            m.session.add(usernotice)
        
        m.session.commit()
        return redirect('/admin/system/notice/')


@module.route('/admin/system/notice/delete/<notice_id>/')
@admin_required
def system_notice_delete(notice_id):
    """删除系统通知"""
    m.session.query(Notice).filter(Notice.id == notice_id).delete()
    m.session.commit()
    return redirect('/admin/system/notice/')


def _get_student_count():
    return m.session.query(User).filter_by(is_student = True).count()

def _get_teacher_count():
    return m.session.query(User).filter_by(is_teacher = True).count()

def _get_parent_count():
    return m.session.query(User).filter_by(is_parent = True).count()

def _get_classgrade_count():
    return m.session.query(Classgrade).count()

def _get_school_count():
    return m.session.query(School).count()

def _get_video_count():
    return m.session.query(Video).count()

def _get_student_count_bystamp(startstamp,endstamp):
    return m.session.query(User).filter_by(is_student = True)\
        .filter(User.created.between(startstamp,endstamp)).count()

def _get_teacher_count_bystamp(startstamp,endstamp):
    return m.session.query(User).filter_by(is_teacher = True)\
        .filter(User.created.between(startstamp,endstamp)).count()

def _get_parent_count_bystamp(startstamp,endstamp):
    return m.session.query(User).filter_by(is_parent = True)\
        .filter(User.created.between(startstamp,endstamp)).count()

def _get_classgrade_count_bystamp(startstamp,endstamp):
    return m.session.query(Classgrade).filter(Classgrade.created.between(startstamp,endstamp)).count()

def _get_school_count_bystamp(startstamp,endstamp):
    return m.session.query(School).filter(School.created.between(startstamp,endstamp)).count()

def _daily_count(start,end):
    days = (end - start).days + 1
    ret = []
    for i in range(days):
        start = startdate + timedelta(i)
        startstamp = dth._begin_stamp(start)
        endstamp = dth._end_stamp(start)
        studentcount = _get_student_count_bystamp(startstamp,endstamp)
        teachercount = _get_teacher_count_bystamp(startstamp,endstamp)
        parentcount = _get_parent_count_bystamp(startstamp,endstamp)
        classcount = _get_classgrade_count_bystamp(startstamp,endstamp)
        schoolcount = _get_school_count_bystamp(startstamp,endstamp)
        ob = dict({'start':start,'studentcount':studentcount,
                   'teachercount':teachercount,'parentcount':parentcount,
                   'classcount':classcount,'schoolcount':schoolcount
                   })
        ret.append(ob)
    return ret

def user_wrapper(user):
    created = dth._stamp_to_date(user.created)
    d = dict({'created':created,'email':user.email,
                  'mobile':user.mobile,'nickname':user.nickname,
                  'is_student':user.is_student,'is_teacher':user.is_teacher,
                  'is_parent':user.is_parent,'user_id':user.user_id})
    if user.is_student:
        d['parent'] = user.parent.nickname if user.parent else ''
        d['classgrades'] = user.classgrades
        d['videoworks'], d['videoworks_approved'] = list_student_videos(user)
    elif user.is_teacher:
        d['classgrades'] = user.classgrades
    elif user.is_parent:
        children = user.children
        d['children'] = dict(map(lambda x:(x.user_id,x.nickname),children))
    return d

def list_users(offset, count):
    users = m.session.query(User).order_by(desc(User.created)).offset(offset).limit(count).all()
    ret = []
    for user in users:
        ret.append(user_wrapper(user))
    return ret

def list_students_notinclass():
    students = m.session.query(User, UserClass).outerjoin(UserClass, User.user_id == UserClass.user_id) \
            .filter(UserClass.id == None, User.is_student == 1).order_by(desc(User.created)).all()
    ret = []
    for student in students:
        user = student.User
        ret.append(user_wrapper(user))
    return ret

def list_unusual_users():
    users = m.session.query(User).filter(or_(User.is_student == 1, User.is_parent == 1)).order_by(desc(User.created)).all()
    ret = []
    for user in users:
        info = user.extra
        if 'parent' not in info and 'children' not in info:
            ret.append(user_wrapper(user))
    return ret

def list_student_videos(user):
    tasks = m.session.query(Taskbox, Works).filter(Taskbox.user_id == user.user_id ) \
            .filter(Taskbox.works_id != None) \
            .join(Task, Taskbox.task_id == Task.task_id). filter(Task.task_type == 1) \
            .join(Works, Taskbox.works_id == Works.works_id). \
            all()
    approved = filter(lambda x: x.Works.parent_approval == 1, tasks)
    return (len(tasks), len(approved))

def list_classes():
    classes = m.session.query(Classgrade,School,UserClass)\
        .outerjoin(School,Classgrade.school_id == School.school_id)\
        .outerjoin(UserClass,UserClass.class_id == Classgrade.class_id)\
        .all()
    creators = filter(lambda x:x.UserClass.is_creator == 1,classes)
    creatorids = map(lambda x:x.UserClass.user_id,creators)
    
    creatormapping = dict(map(lambda x:(x.UserClass.class_id,x.UserClass.user_id),creators))
    
    classcreators = m.session.query(User).filter(User.user_id.in_(creatorids)).all()
    dcreator = dict(map(lambda x:(x.user_id,x),classcreators))
    
    grades = dict(map(lambda x:(x.Classgrade.class_id,x.Classgrade),classes))
    schools = dict(map(lambda x: (x.Classgrade.class_id,x.School),classes))
    dstudent = {}
    dteacher = {}
    for c in classes:
        if c.UserClass and c.UserClass.identity == 0:
            if c.Classgrade.class_id not in dstudent:
                dstudent[c.Classgrade.class_id] = 1
            else:
                dstudent[c.Classgrade.class_id] += 1
        elif c.UserClass and c.UserClass.identity == 1:
            if c.Classgrade.class_id not in dteacher:
                dteacher[c.Classgrade.class_id] = 1
            else:
                dteacher[c.Classgrade.class_id] += 1
    
    classgrades = []
    for cg in grades:
        grade = grades.get(cg)
        school = schools.get(cg)
        cm = creatormapping.get(grade.class_id,'')
        creator = dcreator.get(cm)
        dclass = {'class_id':grade.class_id, 'class_name':grade.class_name,'school_name':school.school_name,
                  'fullname':school.fullname,'studentcount':dstudent.get(cg,0),
                  'teachercount':dteacher.get(cg,0),'creatorname':creator.nickname,'creatoremail':creator.email,
                  'created':grade.created}
        classgrades.append(dclass)
    return classgrades

def list_tasks():
    tasks = m.session.query(ClassTask,Task,User,Classgrade)\
        .outerjoin(Task,Task.task_id == ClassTask.task_id)\
        .outerjoin(User,User.user_id == Task.creator)\
        .outerjoin(Classgrade,Classgrade.class_id == ClassTask.class_id).all()
    classtasks = map(lambda x: {'task_content':x.Task.task_content,'task_type':x.Task.task_type,
                                'class_id':x.Classgrade.class_id, 'task_id':x.Task.task_id,
                                'class_name':x.Classgrade.class_name,'creatorname':x.User.nickname,
                                'creatoremail':x.User.email,'created':x.ClassTask.created},tasks)
    classtasks = sorted(classtasks,key=lambda x:x.get('created'),reverse=True)
    return classtasks

def list_videoworks():
    tasks = m.session.query(Taskbox,Task,User,Works,Video,IndexVideo).filter(Taskbox.works_id != None)\
        .outerjoin(Task,Taskbox.task_id == Task.task_id).filter(Task.task_type == 1)\
        .outerjoin(User,User.user_id == Taskbox.user_id)\
        .outerjoin(Works,Works.works_id == Taskbox.works_id)\
        .outerjoin(IndexVideo,IndexVideo.works_id == Works.works_id)\
        .outerjoin(Video,Video.video_id == IndexVideo.video_id).all()
    
    works = map(lambda x:{'task_content':x.Task.task_content,'username':x.User.nickname,
                          'email':x.User.email,'created':x.Works.created,'thumbnail_path':x.Video.thumbnail_path if x.Video else '',
                          'video_path':x.Video.video_path if x.Video else '','video_id':x.Video.video_id if x.Video else ''},tasks)
    works = sorted(works,key=lambda x:x.get('created'),reverse=True)
    return works


def list_schools(school_type):
    schools = m.session.query(School).filter(School.school_type==school_type)
    schools = schools.order_by(School.created.desc()).all()
    return schools

def list_feedbacks():
    feedbacks = m.session.query(Feedback).order_by(desc(Feedback.created)).all()
    return feedbacks



