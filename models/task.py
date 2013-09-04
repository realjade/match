# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
import time
from sqlalchemy import desc, asc, or_


task = Table("task", metadata, autoload=True)
taskbox = Table("taskbox",metadata, autoload = True)
multitask = Table("multitask", metadata, autoload=True)


class Task(Base, buildmixin('extra')):
    __table__ = task

    @property
    def owner(self):
        from lib.functions import load_user
        return load_user(self.creator)
    
    @property
    def isvideo(self):
        return self.task_type == 1
    
    @property
    def iswriting(self):
        return self.task_type == 2
    
    @property
    def isnotify(self):
        return self.task_type == 3
    
    @property
    def isimage(self):
        return self.task_type == 4
    
    @property
    def istext(self):
        return self.task_type == 5
    
    @property
    def isvalid(self):
        if self.dead_line < time.time()*1000:
            return False
        return True
    
    @property
    def description(self):
        return self.extra.get('description','')
    
    @property
    def remaindays(self):
        remain = self.dead_line - time.time()*1000
        remain =int(remain/1000/60/60/24)
        return remain
    
    def classgrades_model(self):
        """查看该作业发布到几个班级"""
        from models.classgrade import Classgrade,ClassTask
        query = session.query(Classgrade)
        query = query.join(ClassTask, Classgrade.class_id == ClassTask.class_id)
        query = query.filter(ClassTask.task_id == self.task_id)
        return query.all()
    
    @property
    def classgrades(self):
        classes = self.classgrades_model()
        return map(lambda x:{'class_name':x.class_name,'class_id':x.class_id,
                         'created':x.created,'updated':x.updated,'school':x.school},classes)
    
    @staticmethod
    def teacher_notread_count(teacher):
        """老师未批改的作业数量"""
        from models.works import Works
        from lib.functions import SchoolTerm
        term = SchoolTerm()
        query = session.query(Taskbox).filter(Taskbox.works_id != None)
        query = query.join(Task,Taskbox.task_id == Task.task_id)
        query = query.filter(Task.created > term.currentterm)
        query = query.filter(Task.creator == teacher.user_id)
        query = query.join(Works,Taskbox.works_id == Works.works_id)
        notreaded = query.filter(Works.teacher_readed == 0,Works.parent_approval != 0).count()
        return notreaded
    
    @staticmethod
    def student_new_count(student):
        """学生作业数量"""
        from lib.functions import SchoolTerm
        term = SchoolTerm()
        query = session.query(Taskbox)
        query = query.filter(Taskbox.user_id == student.user_id)
        query = query.join(Task,Taskbox.task_id == Task.task_id)
        query = query.filter(Task.created > term.currentterm)
        query = query.filter(Task.task_type.in_((1,4,5)))
        query = query.filter(Taskbox.works_id == None)
        query = query.filter(Taskbox.class_id.in_(student.new_classgrades))
        return query.count()
    
    @staticmethod
    def student_todo_count(student):
        """学生当前作业数量"""
        from models.works import Works
        from lib.functions import SchoolTerm
        term = SchoolTerm()
        query = session.query(Taskbox)
        query = query.filter(Taskbox.user_id == student.user_id)
        query = query.join(Task,Taskbox.task_id == Task.task_id)
        query = query.filter(Task.created > term.currentterm)
        query = query.filter(Task.task_type.in_((1,4,5)))
        query = query.outerjoin(Works,Taskbox.works_id == Works.works_id)
        query = query.filter(or_(Taskbox.works_id == None,Works.teacher_readed == 0))
        query = query.filter(Taskbox.class_id.in_(student.new_classgrades))
        return query.count()
    
    @staticmethod
    def student_notify_count(student):
        """学生未读通知数量"""
        from lib.functions import SchoolTerm
        term = SchoolTerm()
        query = session.query(Taskbox)
        query = query.filter(Taskbox.user_id == student.user_id)
        query = query.filter(Taskbox.confirm == 0)
        query = query.filter(Task.created > term.currentterm)
        query = query.join(Task,Task.task_id == Taskbox.task_id)
        query = query.filter(Task.task_type==3)
        return query.count()
    
    @staticmethod
    def student_writing_count(student):
        """学生未确认笔头作业"""
        from lib.functions import SchoolTerm
        term = SchoolTerm()
        query = session.query(Taskbox)
        query = query.filter(Taskbox.user_id == student.user_id)
        query = query.filter(Taskbox.confirm == 0)
        query = query.join(Task,Task.task_id == Taskbox.task_id)
        query = query.filter(Task.task_type==2)
        query = query.filter(Task.created > term.currentterm)
        return query.count()
    
    
    def _task_type(self):
        if self.isvideo:
            return u'视频'
        if self.iswriting:
            return u'笔头'
        if self.isnotify:
            return u'通知'
        if self.isimage:
            return u'图片'
        if self.istext:
            return u'文字'
    
    def tojson(self, works=None):
        import lib.filters as ft
        from lib import datawrappers as dw
        result = {
                'task_id':self.task_id,
                'task_content':self.task_content,
                'description':self.description,
                'task_type':self.task_type,
                'isvideo':self.isvideo,
                'iswriting':self.iswriting,
                'isimage':self.isimage,
                'istext':self.istext,
                'isvalid':self.isvalid,
                'isnotify':self.isnotify,
                'task_type_text':self._task_type(),
                'classgrades':self.classgrades,
                'need_approval':self.need_approval==1,
                'updatetime':ft.format_datetime(self.updated),
                'deadline':ft.format_datetime(self.dead_line),
                'attachments':dw.wrap_attachments(self.extra.get('attachments',[]),self.extra.get('attachmentdt',None),self.task_id)
                }
        if not works or (works and not works.get("video",{}).get("isfinished",False)):
            result.update({'state':'newwork'})
            if not self.isvalid:
                result.update({'state':'invalid'})
        else:
            result.update({'state':'needapproval'})# 默认显示需要家长点评
            # 如果是学生 没有父母 并且未提交 显示自我点评 result.update({'state':'need-studentapproval'})
            # 如果点评 显示等待教师点评
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
        if works and works.get('created',0)>self.dead_line:
            result.update({'outday':True})
        return result
    
    @staticmethod
    def teacher_task_query(teacher, filter_key="task",class_id=None):
        """
            老师查询发布的作业和通知
            teacher:老师
            filter_key:task作业，notify通知
            class_id:某个班级id
        """
        from models.classgrade import ClassTask
        query = session.query(Task).filter(Task.creator == teacher.user_id)
        if filter_key == 'task':
            query = query.filter(Task.task_type.in_((1,2,4,5)))
        if filter_key == 'notify':
            query = query.filter(Task.task_type ==3)
        if class_id:
            query = query.join(ClassTask,Task.task_id == ClassTask.task_id)
            query = query.filter(ClassTask.class_id == class_id)
        query = query.order_by(Task.created.desc())
        return query
    
    @staticmethod
    def student_task_query(student,filter_key='writing',class_id=None):
        """
            查询学生的笔头作业和通知
            student:学生
            filter_key:notify(通知) writing(笔头作业)
            class_id:班级id
        """
        from models.classgrade import ClassTask
        query = session.query(Taskbox,Task)
        query = query.filter(Taskbox.user_id == student.user_id)
        query = query.join(Task,Taskbox.task_id == Task.task_id)
        if filter_key == 'writing':
            query = query.filter(Task.task_type ==2)
        elif filter_key == 'notify':
            query = query.filter(Task.task_type ==3)
        if class_id:
            query = query.join(ClassTask,Task.task_id == ClassTask.task_id)
            query = query.filter(ClassTask.class_id == class_id)
        query = query.order_by(Task.created.desc())
        return query
        

class Taskbox(Base,buildmixin('extra')):
    __table__ = taskbox
    
    @property
    def classgrade(self):
        from models.classgrade import Classgrade
        return session.query(Classgrade).filter(Classgrade.class_id == self.class_id).first()

class MultiTask(Base, buildmixin('extra')):
    __table__ = multitask
