# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, redirect, render_template, g, current_app,send_file
import models as m
from models.tables import User,Task,Classgrade
import time
import lib.utils as ut
import lib.datawrappers as dw
from lib.wrappers import login_required, parent_required, teacher_required
import lib.functions as f
from lib import videoworks,excel


# Flask 模块对象
module = Blueprint('home', __name__)


@module.route('/home/', methods=['GET'])
@login_required
def home():
    if g.user.isparent:
        return redirect('/parent/addchild/')
    else:
        return redirect('/task/')


@module.route('/teacher/export/',methods=['GET','POST'])
@teacher_required
def teacher_export():
    """
        导出xls文件
    """
    classids = request.values.getlist('classid')
    file= excel.export(classids)
    return send_file(file,as_attachment = True,attachment_filename='export.xls')
