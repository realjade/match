# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, redirect, render_template, g, current_app
import models as m
from models.tables import User, City, School
from sqlalchemy import desc, asc
import time
import lib.utils as ut
from lib.wrappers import admin_required
import lib.functions as f

# Flask 模块对象
module = Blueprint('school', __name__)

@module.route('/school/', methods=['GET', 'POST'])
def school():
    return render_template('school.html',tab='school')

@module.route('/city/list/', methods=['GET', 'POST'])
def city_list():
    cities = m.session.query(City).all()
    cities = map(lambda x:x.tojson(),cities)
    return f.succeed(cities)


@module.route('/school/list/', methods=['GET', 'POST'])
def school_list():
    city = request.values.get('city',None)
    query = m.session.query(School)
    if city:
        query = query.outerjoin(City,School.city_id == City.id).filter(City.name == city)
    schools = query.order_by(desc(School.name)).all()
    schools = map(lambda x:x.tojson(),schools)
    return f.succeed(schools)