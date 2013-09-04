# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
import time
from sqlalchemy import desc, asc, or_


works = Table("works", metadata, autoload=True)

class Works(Base,  buildmixin(('extra','content'))):
    __table__ = works
    
    
    @property
    def user(self):
        from lib.functions import load_user
        return load_user(self.user_id)
    
    @property
    def annotator(self):
        try:
            extradict = self.extra
            annotator = extradict.get('annotator',None)
            return annotator
        except:
            return []
    
    @property
    def isvideo(self):
        try:
            contentdict = self.content
            isvideo = contentdict.get('isvideo',None)
            return isvideo
        except:
            return False

    @property
    def video(self):
        try:
            contentdict = self.content
            video_id = contentdict.get('video_id',None)
            if not video_id:
                return {}
            else:
                from models.video import Video
                video = session.query(Video).filter(Video.video_id == video_id).first()
                import lib.datawrappers as dw
                return dw.wrap_video(video)
        except:
            return {}
    
    @property
    def image(self):
        contentdict = self.content
        image_thumbnail_path = contentdict.get('image_thumbnail_path',[]);
        return {
                'path':json.dumps(contentdict.get('image_path',[])),
                'thumbnail_path':json.dumps(image_thumbnail_path),
                'show_thumbnail_path':image_thumbnail_path[0] if len(image_thumbnail_path)>0 else ''
                }
    
    @property
    def imagelist(self):
        contentdict = self.content
        thun =  contentdict.get('image_thumbnail_path',[])
        path = contentdict.get('image_path',[])
        return zip(thun,path)
    
    @property
    def isfavor(self):
        from models.favor_video import TeacherFavor
        from models.favor_img import TeacherFavorImg
        favor = session.query(TeacherFavor).filter(TeacherFavor.works_id == self.works_id).first()
        if favor:
            return True
        favor = session.query(TeacherFavorImg).filter(TeacherFavorImg.works_id == self.works_id).first()
        if favor:
            return True
        return False
    
    def tojson(self):
        """格式化数据 用于ajax的json加载"""
        from lib import filters as ft
        return {
                'works_id':self.works_id,
                'video':self.video,
                'isapproval':self.parent_approval != 0,
                'parent_comment':self.parent_comment if self.parent_comment else u'家长没有给点评意见哟',
                'isread':self.teacher_readed == 1,
                'teacher_comment':self.teacher_comment if self.teacher_comment != None else u'老师没有给评语',
                'isfavor':self.isfavor,
                'star':int(self.star),
                'updatetime':ft.format_datetime(self.updated),
                'isredo':self.redo == 1,
                'image':self.image
                }
    
    @staticmethod
    def student_works_query(student, filter_key='readed',class_id=None,currentterm=None):
        """
            查询学生的作业
                student: 学生
                filter_key: readed(已读) notreaded(未读)
                class_id:班级
                currentterm:某日期之前的作业 SchoolTerm类的计算
        """
        from models.task import Task, Taskbox
        query = session.query(Taskbox,Task,Works)
        query = query.filter(Taskbox.user_id == student.user_id)
        if class_id:
            query = query.filter(Taskbox.class_id == class_id)
        query = query.join(Task,Taskbox.task_id == Task.task_id)
        if currentterm:
            query = query.filter(Task.created > currentterm)
        query = query.filter(Task.task_type.in_((1,4,5)))
        
        if filter_key == "readed":
            query = query.join(Works,Taskbox.works_id == Works.works_id)
            query = query.filter(Works.teacher_readed == 1)
            query = query.filter(Works.redo == 0)
        elif filter_key == "notreaded":
            or_filter = or_(Taskbox.works_id == None,
                            Works.teacher_readed == 0,
                            Works.redo == 1)
            query = query.outerjoin(Works,Taskbox.works_id == Works.works_id).filter(or_filter)
            query = query.filter(Taskbox.class_id.in_(student.new_classgrades))
        else:
            raise KeyError("filter_key not exist")
        query = query.order_by(Task.created.desc())
        return query
        
    @staticmethod
    def teacher_works_query(teacher, filter_key="readed",task_id = None,currentterm=None):
        """
            查询老师发布的作业
                teacher:老师
                filter_key: readed(已批改),notreaded(未批改)
                task_id:某个作业（批改同主题作业）
                currentterm:某日期之前的作业 SchoolTerm类的计算
        """
        from models.task import Task, Taskbox
        query = session.query(Taskbox,Task,Works)
        query = query.filter(Taskbox.works_id != None)
        query = query.join(Task,Taskbox.task_id == Task.task_id)
        if task_id:
            query = query.filter(Task.task_id == task_id)
        query = query.filter(Task.created > currentterm)
        query = query.filter(Task.creator == teacher.user_id)
        query = query.join(Works,Taskbox.works_id == Works.works_id)
        query = query.filter(Works.parent_approval != 0)
        if filter_key == 'readed':
            query = query.filter(Works.teacher_readed == 1)
        elif filter_key == 'notreaded':
            query = query.filter(Works.teacher_readed == 0)
        else:
            raise KeyError("filter_key not exist")
        query = query.order_by(Task.created.desc(),Works.updated.desc())
        return query
    
    
    
