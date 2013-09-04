# -*- coding: utf-8 -*-
from engine_script import session
from models.tables import User, Classgrade, UserClass, Task
import time
from werkzeug import generate_password_hash
from datetime import datetime
"""
    增加系统教师角色 可反复执行
"""
user_id = u'1000000000'
user_nickname = u'智慧超人'
user_email = u'sunchao@beishu8.com'
user_mobile = u''
user_password = u'vself888888'
user_course = u'助教'
task_id = u"4000000000000"
task_content = u"小朋友，刚刚加入背书吧的大家庭，做个自我介绍吧！"
task_desc = u"录制一段一分钟左右的中文视频，介绍一下自己的名字，居住的城市，学习的学校，兴趣爱好，最要好的朋友。和老师，和大家认识一下吧！"
needapproval = 1
tasktype = 1 # 视频作业


if __name__ == "__main__":
    user = session.query(User).filter(User.user_id == user_id).first()
    print "========get system teacher========"
    print user
    if not user:
        print "========create system teacher========"
        user = User(user_id = user_id,
                nickname=user_nickname, email=user_email ,mobile=user_mobile,
                pw_hash=generate_password_hash(user_password),
                is_teacher= 1, is_student=0,is_parent=0,
                created=int(time.time()*1000), updated=int(time.time()*1000))
        user.extra.update({'course':user_course})
        session.add(user)
        session.commit()
        print user
    else:
        print "========update system teacher========"
        user.nickname = user_nickname
    
    print "========delete system teacher join classgrade========"
    session.query(UserClass).filter(UserClass.user_id==user.user_id).delete()
    
    print u"========create task========"
    task = session.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        task = Task(task_id = task_id, task_content = task_content,
            need_approval = needapproval, task_type = tasktype, creator = user_id,
            created = int(time.time()*1000), updated = int(time.time()*1000))
        task.dead_line=time.mktime(datetime(2020,12,31,23,59,59).timetuple())*1000
        session.add(task)
        print u"========create task ok========"
    else:
        print u"========update task========"
        task.task_content = task_content
        task.dead_line=time.mktime(datetime(2020,12,31,23,59,59).timetuple())*1000
        task.extra['description'] = task_desc
    session.commit()
    
