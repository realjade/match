# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, session, url_for, redirect, render_template, g, abort
from werkzeug import check_password_hash
import lib.functions as f
from models.tables import User

"""
    登录
"""

module = Blueprint('login', __name__)


@module.route('/', methods=['GET', 'POST'])
def index():
    """Logs the user in."""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        remember = request.form.get('remember', None) == 'on'
        password = request.form['password']
        user = User.get_user(username)
        if user is None:
            error = u'邮箱或者手机号不正确'
        elif not user.check_password_hash(password):
            error = u'密码不正确'
        else:
            session['user_id'] = user.user_id
            if remember:
                session.permanent = True
            if user.isparent and user.children:
                return redirect('/task/notreaded/%s/' % user.children[0])
            return redirect(url_for('home.home'))
    if g.user:
        return redirect(url_for('home.home'))
    
    if request.environ['HTTP_HOST'] == "demo.beishu8.com":
        return render_template('demo.html')
    else:
        return render_template('index.html', error=error)


@module.route('/login/')
def login():
    return redirect(url_for('login.index'))


@module.route('/logout/')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('.index'))


@module.route("/demo/teacher/login/", defaults = {"identity":"teacher"})
@module.route("/demo/student/login/", defaults = {"identity":"student"})
@module.route("/demo/parent/login/", defaults = {"identity":"parent"})
def demo_login(identity):
    if request.environ['HTTP_HOST'] == "demo.beishu8.com":
        dt = {"teacher":"1128645876","student":"1275953415","parent":"1948556306"}
        session['user_id'] = dt[identity]
        return redirect(url_for('home.home'))
    elif request.environ['HTTP_HOST'] == "0.0.0.0:9000":
        dt = {"teacher":"1231282854","student":"1956016767","parent":"1173149772"}
        session['user_id'] = dt[identity]
        return redirect(url_for('home.home'))
    else:
        abort(404)
