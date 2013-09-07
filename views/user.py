# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, redirect, render_template, g, current_app,send_file
import models as m
from models.tables import User
import time
import lib.utils as ut
from lib.wrappers import admin_required
import lib.functions as f

# Flask 模块对象
module = Blueprint('user', __name__)

@module.route('/user/list/', methods=['GET', 'POST'])
@admin_required
def user_list():
    return render_template('user/user.html', tab='match')

@module.route('/user/add/', methods=['GET', 'POST'])
@admin_required
def user_add():
    return render_template('user/user.html', tab='match')

@module.route('/user/remove/', methods=['GET', 'POST'])
@admin_required
def user_remove():
    return render_template('user/user.html', tab='match')

@module.route('/user/update/', methods=['GET', 'POST'])
@admin_required
def user_update():
    return render_template('user/user.html', tab='match')