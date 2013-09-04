# -*- coding: utf-8 -*-
from functools import wraps
from flask import request,Response, g, session, redirect, url_for, current_app, json
import types
import models as m
from models.admin import Admin

def jsonp_wrapper(r):
    cb = request.values.get('callback')
    if cb:
        return '%s(%s);'%(cb, r)
    else:
        return r

def jsonify(fn):
    @wraps(fn)
    def jsonify_wrapped(*args, **kwargs):
        ret = fn(*args, **kwargs)
        if type(ret) == types.DictionaryType:
            r = json.dumps({"code":'0', "data":ret})
            return jsonp_wrapper(r.decode('raw_unicode_escape').encode('utf-8'))
        elif type(ret) in [types.TupleType, types.ListType] and len(ret) >= 2:
            return jsonp_wrapper(json.dumps({"code":ret[0], "message":ret[1]}))
        elif isinstance(ret, Response):
            if ret.status_code/100 == 3:
                return jsonp_wrapper(json.dumps({"code":'%d'%(ret.status_code), "message":ret.headers['locaction']}))
            else:
                return jsonp_wrapper(json.dumps({"code":'%d'%(ret.status_code), "message":ret.status}))
        else:
            return jsonp_wrapper(json.dumps({"code":'0', "data":"%s"%(ret)}))
    return jsonify_wrapped


def admin_required(fn):
    @wraps(fn)
    def admin_wrapped(*argt, **argd):
        admin = None
        if g.user:
            admin = m.session.query(Admin).filter(Admin.user_id == g.user.user_id).first()
        if not g.user or not admin:
            return redirect(url_for('login.login',next = request.url))
        ret = fn(*argt, **argd)
        return ret
    return admin_wrapped

def login_required(fn):
    @wraps(fn)
    def login_wrapped(*argt, **argd):
        if g.user is None:
            return redirect(url_for('login.login', next=request.url))
        ret = fn(*argt, **argd)
        return ret
    return login_wrapped

def parent_required(fn):
    @wraps(fn)
    def parent_wrapped(*argt, **argd):
        if g.user is None or not g.user.isparent:
            return redirect(url_for('login.login', next=request.url))
        ret = fn(*argt, **argd)
        return ret
    return parent_wrapped

def teacher_required(fn):
    @wraps(fn)
    def teacher_wrapped(*argt, **argd):
        if g.user is None or not(g.user.isteacher):
            return redirect(url_for('login.login', next=request.url))
        ret = fn(*argt, **argd)
        return ret
    return teacher_wrapped


def student_required(fn):
    @wraps(fn)
    def student_wrapped(*argt, **argd):
        if g.user is None or not g.user.isstudent:
            return redirect(url_for('login.login', next=request.url))
        ret = fn(*argt, **argd)
        return ret
    return student_wrapped



def m_login_required(fn):
    @wraps(fn)
    def login_wrapped(*argt, **argd):
        if g.user is None:
            return redirect(url_for('mobile.m_login', next=request.url))
        if g.user.isparent:
            return redirect(url_for('mobile.m_selectchild'))
        g.parent = None
        if 'parent_id' in session:
            import lib.functions as f
            g.parent = f.load_user(session['parent_id'])
        ret = fn(*argt, **argd)
        return ret
    return login_wrapped
