# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, session, url_for, redirect, \
        render_template, abort, g, flash, json, Response, make_response, current_app,send_file
import models as m
from models.tables import User,Admin,Classgrade,Task,Video,Works,School,TeacherFavor,\
        Taskbox,ClassTask,UserClass,TimeLine,Feedback
from werkzeug import check_password_hash, generate_password_hash
from werkzeug import secure_filename
from sqlalchemy import or_,desc
import time
import pickle
import lib.utils as ut
from lib.wrappers import login_required, parent_required, teacher_required, student_required, jsonify
import lib.functions as f
import lib.filters as flt
from lib.videohelper import VideoHelper
from lib import const, videoworks
import os
import string
from random import choice
import types
import Image

"""
    该模块暂时为手机请求视图
"""

module = Blueprint('mapi', __name__)

@module.route("/mapi/login/",methods=['GET', 'POST'])
@jsonify
def mapi_login():
    username = request.values['username']
    remember = request.values.get('remember', None) == 'on'
    user = User.get_user(username)
    usertype = ''
    useravatar = ''
    if user is None:
        return const.ACCOUNT_NOT_EXIST
    elif not check_password_hash(user.pw_hash,
                                 request.values['password']):
        return const.INVALID_PASSWORD
    else:
        if user.isparent:
            usertype = "parent"
        elif isteacher:
            usertype = 'teacher'
        else:
            usertype = 'student'
        useravatar = flt.avatar(user,'big')
        session['user_id'] = user.user_id
        if remember:
            session.permanent = True
    return {'user_id':user.user_id, 'type':usertype, 'avatar':useravatar}

