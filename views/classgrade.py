# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request,redirect,render_template, g, current_app,abort
from werkzeug.datastructures import Headers
from models.tables import Demand, ClassDemand, Classgrade, User, School, UserClass, Task,Taskbox, Works, TeacherFavor,Video,IndexVideo
from lib.wrappers import login_required, teacher_required
import lib.functions as f
import lib.utils as ut
from lib import const,mail,sms
import models as m
import time
from datetime import datetime
from flask.ext.sqlalchemy import Pagination
from lib import datawrappers as dw


# Flask 模块对象
module = Blueprint('classgrade', __name__)


@module.route('/class/',methods=['GET'])
@module.route('/class/<class_id>/', methods=['GET'])
@module.route('/class/<class_id>/info/', methods=['GET'])
@login_required
def classgrade(class_id=None):
    """ 
        班级管理
        班级信息
    """
    user = g.user
    if user.isteacher or user.isstudent:
        if class_id:
            classes = [user.classgrade_model(class_id)]
        else:
            classes = user.classgrades_model()
        rekwargs = {"classes" : map(lambda x:x.tojson({'isteacher':True} if user.isteacher else {}),classes), "tab" : "class"}
        if class_id:
            rekwargs["subtab"] = class_id
            rekwargs["innertab"] = "info"
            rekwargs["classup"] = True
        return render_template('school/class/info.html', **rekwargs)
    else:
        return redirect("/")


@module.route('/class/<class_id>/members/')
@login_required
def members(class_id=None):
    """班级管理>所有成员"""
    classgrade = m.session.query(Classgrade).filter(Classgrade.class_id == class_id).first()
    return render_template('school/class/members.html',
                    tab = 'class',
                    classgrade = classgrade,
                    subtab = class_id,
                    innertab='members')


@module.route('/class/<class_id>/member/<member_id>/')
@login_required
def student_info(class_id,member_id):
    """班级管理>所有成员>查看班级同学"""
    member = m.session.query(User).filter(User.user_id == member_id).first()
    if member and member.isstudent:
        page = int(request.args.get("page","1"))# 当前页
        query = Works.student_works_query(member, filter_key='readed', class_id=class_id)
        count = query.count()
        workslist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
        pagination = Pagination(query,page,30,count,workslist)# 每页30个
        workslist = []
        for taskbox,task,works in pagination.items:
            teacher = f.load_user(task.creator)
            worksjson = works.tojson()
            data = {'works':worksjson}
            userjson = member.tojson()
            data.update(userjson)
            data.update(userjson)
            data.update(teacher = teacher.tojson())
            data.update(task = task.tojson(worksjson))
            workslist.append(data)
        return render_template('school/class/member_info.html',
                                    pagination = pagination,
                                    workslist = workslist,
                                    page=page,
                                    member = member,
                                    tab = 'class',
                                    subtab = class_id)
    else:
        abort(404)


@module.route('/class/member/delete/', methods=['POST'])
@teacher_required
def member_delete():
    """班级管理>所有成员>删除班级成员"""
    member_id = request.form.get('member_id',None)
    class_id = request.form.get('class_id',None)
    if not member_id or not class_id:
        return f.failed(*const.INVALID_PARAMS)
    # 判断是否是该班级的老师
    classgrade = m.session.query(Classgrade).filter(Classgrade.class_id == class_id).first()
    if not classgrade:
        return f.failed(*const.ClASS_NOT_EXIST)
    teacher = m.session.query(UserClass).filter(UserClass.user_id == g.user.user_id).first()
    if not teacher:
        return f.failed(*const.ClASS_NOT_EXIST)
    query = m.session.query(UserClass)
    query = query.filter(UserClass.user_id == member_id)
    query.filter(UserClass.class_id == class_id).delete()
    content = u"你已被%s老师退出%s，如果有疑问，请与老师联系。" % (g.user.nickname,classgrade.class_name)
    task = Task(task_id = ut.create_task_id(), task_content = content,
        dead_line = time.mktime(datetime(2020,12,31,23,59,59).timetuple())*1000,
        need_approval = 1, task_type = '3', creator = g.user.user_id,
        created = int(time.time()*1000), updated = int(time.time()*1000))
    m.session.add(task)
    taskbox = Taskbox(task_id = task.task_id, user_id = member_id, class_id = class_id,confirm = 0,
             created = int(time.time()*1000), updated = int(time.time()*1000))
    m.session.add(taskbox)
    m.session.commit()
    return f.succeed("ok")


@module.route('/class/<class_id>/demand/', methods=['GET'])
@login_required
def demand(class_id=None):
    """班级管理>新学期新要求"""
    query = m.session.query(Demand)
    query = query.filter(Demand.creator == g.user.user_id)
    demandli = query.order_by(Demand.created.desc()).all()
    return render_template('school/class/demand.html',
                    demandli = demandli,
                    tab = 'class',
                    subtab = class_id,
                    innertab='demand')


@module.route('/class/<class_id>/demand/', methods=['POST'])
@teacher_required
def demand_post(class_id):
    """班级管理>新学期新要求>创建"""
    name = request.form['name']
    content = request.form["content"]#.replace("\n","&#60;br /&#62;")# "&lt;br /&gt;"
    classes = request.form.getlist("classes")
    demand = Demand(name = name, content = content,creator = g.user.user_id,
                demand_id = ut.create_demand_id(),
                created=int(time.time()*1000), updated=int(time.time()*1000))
    m.session.add(demand)
    for class_id in classes:
        classdemand = ClassDemand(demand_id = demand.demand_id,class_id = class_id,
                        created=int(time.time()*1000), updated=int(time.time()*1000))
        m.session.add(classdemand)
    m.session.commit()
    return redirect("/class/%s/demand/" % class_id)



@module.route('/class/<class_id>/demand/<demand_id>/delete/', methods=['GET'])
@teacher_required
def demand_delete(class_id,demand_id):
    """班级管理>新学期新要求>删除"""
    m.session.query(Demand).filter(Demand.demand_id == demand_id).delete()
    m.session.query(ClassDemand).filter(ClassDemand.demand_id == demand_id).delete()
    m.session.commit()
    return redirect("/class/%s/demand/" % class_id)


@module.route('/class/<class_id>/history/', methods=['GET'])
@login_required
def history(class_id):
    """班级管理>历史学期"""
    user = g.user
    term = f.SchoolTerm()
    page = int(request.args.get("page","1"))# 当前页
    year = int(request.args.get("year",term.yearlist[-1]))
    month = int(request.args.get("month",5 if term.termlist[-1][-1]==1 else 10))
    if month == 5:
        stime,etime = term.analyze(year+1,month)
    else:
        stime,etime = term.analyze(year,month)
    if user.isteacher:
        nickname = request.args.get("nickname",None)
        task_content = request.args.get("task_content")
        favor = int(request.args.get("favor","0"))
        
        query = m.session.query(Taskbox,Task,User,Works,Video)# 返回对象
        query = query.filter(Taskbox.class_id == class_id)# 班级
        query = query.join(Works, Works.works_id == Taskbox.works_id)
        query = query.filter(Works.teacher_readed == 1)# 老师批改完成
        if favor:# 推荐视频
            query = query.join(TeacherFavor, TeacherFavor.works_id == Works.works_id)
        #video
        # TODO 图片检查未做 去掉视频搜索根据Task查询判断显示
        query = query.join(IndexVideo, Works.works_id == IndexVideo.works_id)
        query = query.join(Video, IndexVideo.video_id == Video.video_id)
        query = query.join(Task,Taskbox.task_id == Task.task_id)
        query = query.filter(Task.task_type == 1)#TODO Task.task_type.in_([1,4])
        query = query.filter(Task.creator == user.user_id)
        query = query.filter(Task.created >= stime)
        query = query.filter(Task.created < etime)
        query = query.join(User,Taskbox.user_id == User.user_id)
        
        if task_content:
            query = query.filter(Task.task_content.like("%%%s%%" % task_content))
        if nickname:
            query = query.filter(User.nickname.like("%%%s%%" % nickname))
        query = query.order_by(Task.created.desc(),Taskbox.updated.desc())
        count = query.count()
        taskboxlist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
        pagination = Pagination(query,page,30,count,taskboxlist)# 每页30个
        return render_template('school/class/history_teacher.html',
                    tab = 'class',
                    subtab = class_id,
                    innertab='history',
                    pagination = pagination,
                    nickname = nickname,
                    task_content = task_content,
                    year = year,
                    month = month,
                    yearlist = term.yearlist,
                    favor = favor)
    elif user.isstudent:
        teacherid = request.args.get("teacherid","0")
        stype = request.args.get("stype","1")
        classgrade = m.session.query(Classgrade).filter(Classgrade.class_id == class_id).first()
        
        query = m.session.query(Taskbox,Task,User,Works,Video)
        query = query.filter(Taskbox.class_id == class_id)# 班级
        
        query = query.join(Works, Works.works_id == Taskbox.works_id)
        query = query.filter(Works.teacher_readed == 1)# 老师批改完成
        #TODO img
        query = query.join(IndexVideo, Works.works_id == IndexVideo.works_id)
        query = query.join(Video, IndexVideo.video_id == Video.video_id)
        query = query.join(Task,Taskbox.task_id == Task.task_id)
        query = query.filter(Task.task_type == 1)#TODO Task.task_type.in_([1,4])
        if teacherid != "0":
            query = query.filter(Task.creator == teacherid)
        if stype == "2":
            query = query.join(TeacherFavor, TeacherFavor.works_id == Works.works_id)
        else:
            query = query.filter(Taskbox.user_id == user.user_id)
        query = query.filter(Task.created >= stime)
        query = query.filter(Task.created < etime)
        query = query.join(User,Taskbox.user_id == User.user_id)
        query = query.order_by(Task.created.desc(),Taskbox.updated.desc())
        count = query.count()
        taskboxlist = query.offset(page*30 - 30).limit(30).all()# 查询的具体数据
        pagination = Pagination(query,page,30,count,taskboxlist)# 每页30个
        return render_template('school/class/history_student.html',
                    tab = 'class',
                    subtab = class_id,
                    innertab='history',
                    pagination = pagination,
                    teacher = classgrade.teacher,
                    year = year,
                    month = month,
                    yearlist = term.yearlist,
                    teacherid = teacherid,
                    stype = stype)
    else:
        return redirect("/")










@module.route('/class/create/')
@teacher_required
def class_create():
    """创建班级"""
    return render_template('school/class_create.html', tab = 'class', subtab = 'create')


@module.route('/class/join/', methods=['GET'])
@login_required
def class_join():
    """加入班级"""
    return render_template('school/class_join.html', tab = 'class', subtab = 'join')





@module.route('/class/invitation/email/', methods=['POST'])
@login_required
def clss_inv_email():
    """发送邀请信到公共邮箱"""
    class_id = request.form.get('class_id','')
    classgrade = m.session.query(Classgrade).filter(Classgrade.class_id==class_id).first()
    if classgrade:
        if classgrade.email:
            success = mail.smtp_send_mail([classgrade.email], {'event':'invitataion',
                                        'class_code':class_id,
                                        'class_name':classgrade.class_name})
            if success:
                return f.succeed({})
        else:
            return f.failed(*const.ClASS_EMAIL_NOT_EXIST)
    return f.failed({})


@module.route('/class/download/invitation/<class_id>/')
@login_required
def download_invitation(class_id):
    """下载邀请信"""
    classgrade = m.session.query(Classgrade).filter(Classgrade.class_id==class_id).first()
    if not classgrade:
        abort(404)
    
    data = u"""登录网址：beishu8.com 班级号：%s\r\n\r\n各位家长：
\r\n培养孩子良好的学习习惯、自信和自制能力，需要我们和您的共同努力。
\r\n为了及时的与您沟通、更好的让孩子完成老师布置的每项作业、引导孩子健康安全的上网，我班现开始免费使用背书吧平台给孩子布置作业。在这一过程中，老师会把每天的视频作业和通知通过背书吧发布，您在家中将协助学生或者让学生独立完成视频作业，确认笔头作业和通知，并通过这一渠道和老师直接沟通，老师也会与您保持紧密的联系。
\r\n请您登录www.beishu8.com，用真实姓名注册家长账户和学生账户，加入所在的班级，随后完成老师布置的笔头、听说作业。在网站的首页，有关于注册和使用的视频帮助文件，请您仔细观看。希望各位家长能够在百忙之中抽出碎片时间，随时随地每天登陆网站查看和审核孩子的作业，帮助孩子录制听说视频作业。为孩子留下美好的视频回忆。
\r\n任何一种新产品的诞生，都会让使用者在最初觉得不便，在此，我们感到非常抱歉，当您熟练使用背书吧以后，您会发现，每天您花在背书吧上的时间，不会超过15分钟。
\r\n如遇使用问题请致电400-015-3066咨询解决。感谢各位家长，与我们共同引导、监督和帮助您的孩子。
\r\n----------------------------------------------------------
\r\n\r\n语言学习、表达能力的问题
\r\n目前的教学系统中，学生读和背的量化问题一直无法很好的解决，尤其在语言学习方面，孩子们能够很好的完成笔头作业，而口头作业总是没有办法很好的完成并检查，这就导致了孩子们在文字写作方面的能力逐步提升，而口头表达能力却无法提高，哑巴英语、不自信，不敢在众人面前发言、不会沟通成为未来孩子学习和工作中非常严重的问题，我们经常看到孩子在全班同学面前讲话的时候，不知道看哪里，小动作和口头语又特别多，这让我们感到非常心焦。
\r\n\r\n家校沟通不畅的问题
\r\n家长总是从孩子口中得到关于通知、作业等信息，无法直接从老师这里获得，而家长会只能每学期开一次，这就给了学生钻空子的机会，或者少说，或者不说，直接导致了老师和家长之间的信息不对称，也直接影响了您对学生学习情况的了解。
\r\n\r\n青少年健康安全上网问题
\r\n中国青少年健康安全上网问题越来越严重，作为老师和家长，我们有责任在这一过程中采用正确的方法引导孩子们，然而我们真的有能力做到这一点吗？我们是否对网络的了解也是一知半解，除了百度、淘宝、QQ以外，我们又有什么东西可以教给孩子们呢？大部分家长采用不让孩子们上网的方法进行控制，这是不正确的，孩子们在长大后一定会使用网络的，我们应该在他们自我摸索之前找到一种方法，帮助和引导孩子们正确上网。
\r\n----------------------------------------------------------""" % (class_id,)
    filename = u"%s邀请信.txt" % classgrade.class_name
    headers = Headers()
    headers.add('Content-Disposition', 'attachment',
                    filename=filename.encode("gb2312"))
    headers['X-Sendfile'] = 'filename'
    headers['Content-Length'] = len(data)
    mimetype = 'application/octet-stream'
    rv = current_app.response_class(data, mimetype=mimetype, headers=headers,
                                    direct_passthrough=True)
    return rv


@module.route('/invite-mail/', defaults={'template':'invite-mail.html'})
@login_required
def invite_mail(template):
    """邀请信打印功能"""
    class_id = request.values.get('code','')
    class_info = None
    classgrade = m.session.query(Classgrade).filter(Classgrade.class_id == class_id).first()
    if classgrade:
        class_info ={'class_id':classgrade.class_id,'class_name':classgrade.class_name,
                        'school_name':classgrade.school, 
                      'description':classgrade.extra.get('description','')}
    return render_template('school/class/%s' % template, class_info = class_info)



