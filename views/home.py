# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, redirect, render_template, g, current_app,send_file
import models as m
from models.tables import User
import time
import lib.utils as ut
from lib.wrappers import login_required, parent_required, teacher_required
import lib.functions as f

# Flask 模块对象
module = Blueprint('home', __name__)

@module.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')