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
from lib import const

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

@module.route('/school/add/', methods=['GET', 'POST'])
def school_add():
    city_id = request.values.get('cityid',None)
    name = request.values.get('name',None)
    if not city_id or not name:
        return f.failed(*const.INVALID_PARAMS)
    school = f.load_school_by_name(name,city_id)
    if school:
        return f.failed(*const.SCHOOL_EXIST)
    school = School(city_id = city_id, name = name, created = int(time.time()*1000), updated = int(time.time()*1000))
    m.session.add(school)
    m.session.commit()
    return f.succeed(school.tojson())

@module.route('/school/update/', methods=['GET', 'POST'])
def school_update():
    school_id = request.values.get('schoolid',None)
    name = request.values.get('name',None)
    if not school_id or not name:
        return f.failed(*const.INVALID_PARAMS)
    school = m.session.query(School).filter(School.id == school_id).first()
    if not school:
        return f.failed(*const.SCHOOL_NOT_EXIST)
    if school.name == name:
        return f.failed(*const.INVALID_PARAMS)
    hasSchool = f.load_school_by_name(name,school.city_id)
    if hasSchool:
        return f.failed(*const.SCHOOL_NOT_EXIST)
    school.name = name
    school.updated = time.time()*1000
    m.session.commit()
    return f.succeed(school.tojson())