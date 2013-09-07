# -*- coding: utf-8 -*-
import os
import utils as ut
from flask import json, g, request, session
import models as m
from models.tables import User, School, Team, Match, City
from sqlalchemy import or_, func, distinct
from sqlalchemy import desc, asc
from sqlalchemy.orm import aliased
import time
from datetime import datetime
import types
import lib.filters as ft
import math
from cache import context_cached, redis_cached


def succeed(data):
    return json.dumps({"code":0, "data":data})

def failed(code, message):
    return json.dumps({"code":code, "message":message})

def paginated(query,column,count=-1, offset=-1, **kwargs):
    query = query.order_by(desc(column))
    if count > 0:
        query = query.limit(count)
    
    if offset > 0:
        query = query.offset(offset)

    result = query.all()
    return result

def pages(func, *args, **kwargs):
    page = {}
    curpage = request.args.get('page',1)
    if not curpage:
        curpage = 1
    curpage = int(curpage)
    count = 30
    kwargs.update(count=count)
    kwargs.update(offset=(curpage-1)*count)
    results,total = func(*args, **kwargs)
    page.update({'curpage':int(curpage),'pages':int(math.floor(total/count)+1),'total':int(total)})
    return results,page

@context_cached()
def load_user(user_id):
    return m.session.query(User).filter(User.id == user_id).first()

@context_cached()
def load_school(school_id):
    return m.session.query(School).filter(School.id == school_id).first()

@context_cached()
def load_school_by_name(school_name,city_id):
    return m.session.query(School).filter(School.name == school_name,School.city_id == city_id).first()


def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in set(['avi', 'flv', 'f4v', 'mp4', 'm4v', 'mkv', 
        'mov', '3gp', '3gp', '3g2', 'mpg', 'wmv', 'ts'])

def allowed_img_file(filename):
    extli = ['png', 'jpg', 'jpeg', 'gif']
    upextli = [ext.upper() for ext in extli]
    extli.extend(upextli)
    return '.' in filename and filename.rsplit('.', 1)[1] in set(extli)

def allowed_excel(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in set(['xls', 'xlsx'])


def time_filter(query, column, starttime, endtime):
    if starttime > 0:
        query = query.filter(column > starttime)
    if endtime > 0:
        query = query.filter(column < endtime)
    return query

