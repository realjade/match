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
module = Blueprint('team', __name__)

@module.route('/team/', methods=['GET', 'POST'])
@admin_required
def team():
    return render_template('team/team.html',tab='team')