# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, session, url_for, redirect, render_template, g
import lib.functions as f
from lib.wrappers import login_required, teacher_required
"""
    登录
"""

videolist = [
    ("manage_class_convert.mp4","manage_class_convert.jpg",u"班级管理"),
    ("send_task_convert.mp4","send_task_convert.jpg",u"发布作业和通知"),
    ("pigai_convert.mp4","pigai_convert.jpg",u"批改作业"),
    ("reportcard_favor_convert.mp4","reportcard_favor_convert.jpg",u"成绩单和秀场"),
    ("student_help_convert.mp4","student_help_convert.jpg",u"家长使用指南"),
    ]


module = Blueprint('help', __name__)

@module.route("/help/video/<index>/")
@teacher_required
def video(index):
    return render_template("help/index.html",videolist=videolist,index = index)


@module.route("/help/student/video/<index>/")
@login_required
def student_video(index):
    return render_template("help/student.html",videolist=videolist[-1:],index=index)


