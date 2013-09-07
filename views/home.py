# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, redirect, render_template, g, current_app,send_file, url_for
import models as m
from models.tables import User
import time
import lib.utils as ut
from lib.wrappers import admin_required
import lib.functions as f

# Flask 模块对象
module = Blueprint('home', __name__)

@module.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('login.login'))