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


@module.route('/xx', methods=['GET', 'POST'])
def xx():
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