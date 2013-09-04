# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import render_template, g, request, url_for, redirect
import models as m
from models.tables import IreadCount
from datetime import datetime, timedelta
import time
import lib.functions as f


module = Blueprint('iread', __name__)

@module.route('/iread/index/', methods=['GET'],defaults={"template":"iread/index.html"})
def index(template):
    # 统计信息
    ireadcount = IreadCount()
    if g.user:
        ireadcount.user_id = g.user.user_id
    else:
        ireadcount.user_id = request.remote_addr
    ireadcount.created = int(time.time()*1000)
    m.session.add(ireadcount)
    m.session.commit()
    return render_template(template)


@module.route('/iread/foodstay/', methods=['GET'],defaults={"template":"iread/foodstay.html"})
@module.route('/iread/schedule/', methods=['GET'],defaults={"template":"iread/schedule.html"})
@module.route('/iread/day1/', methods=['GET'],defaults={"template":"iread/day1.html"})
@module.route('/iread/day2/', methods=['GET'],defaults={"template":"iread/day2.html"})
@module.route('/iread/day3/', methods=['GET'],defaults={"template":"iread/day3.html"})
@module.route('/iread/day4/', methods=['GET'],defaults={"template":"iread/day4.html"})
@module.route('/iread/day5/', methods=['GET'],defaults={"template":"iread/day5.html"})
@module.route('/iread/day6/', methods=['GET'],defaults={"template":"iread/day6.html"})
@module.route('/iread/day7/', methods=['GET'],defaults={"template":"iread/day7.html"})
@module.route('/iread/day8/', methods=['GET'],defaults={"template":"iread/day8.html"})
def iread(template):
    return render_template(template)



