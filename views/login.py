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


@module.route('/login/', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    error = None
    if request.method == 'POST':
        mobile = request.form['mobile']
        remember = request.form.get('remember', None) == 'on'
        password = request.form['password']
        user = User.get_user(mobile)
        if user is None:
            error = u'手机号不正确'
        elif not user.check_password_hash(password):
            error = u'密码不正确'
        elif not user.isAdmin:
            error = u'您不是管理员'
        else:
            session['user_id'] = user.id
            if remember:
                session.permanent = True
            return redirect(url_for('team.team'))
    if g.user and g.user.isAdmin:
        return redirect(url_for('team.team'))
    return render_template('login.html', error=error)



@module.route('/logout/')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('.login'))