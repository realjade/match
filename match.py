# -*- coding: utf-8 -*-

from flask import Flask, g, session,url_for, redirect
from datetime import datetime
from hashlib import md5
from redis import Redis
from rsession import RedisSessionInterface
import types
import config
from assets import Assets
from random import choice
import string


from flask import Flask
app = Flask("match")
app.config.from_object(config)
app.redis = Redis(app.config['REDIS_HOST'], app.config['REDIS_PORT'], app.config['REDIS_DB'], app.config['REDIS_PASSWORD'])
app.session_interface = RedisSessionInterface(app.redis)

assets = Assets(app)

import models
models.setup(app)

from views import login, home, team, match, user, school

app.register_blueprint(login.module)
app.register_blueprint(home.module)
app.register_blueprint(team.module)
app.register_blueprint(match.module)
app.register_blueprint(user.module)
app.register_blueprint(school.module)


from lib import filters
filters.setup(app)


from flask import render_template
from flask import request

@app.errorhandler(404)
def page_not_found(error):
    if request.path.startswith('/static/'):
        return error, 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_internal_error(error):
    import traceback
    app.logger.error('='*60)
    app.logger.error(traceback.format_exc())
    app.logger.error('='*60)
    return render_template('500.html')
        
# 设置logger的输出形式
import logging, os 
from logging.handlers import TimedRotatingFileHandler 
#base = os.path.abspath(os.path.dirname(__file__)) 
log_root = app.config.get('LOG_PATH', 'logs')
logfile = os.path.join(os.path.abspath(log_root), 'match.log') 
handler = TimedRotatingFileHandler(filename=logfile, when='MIDNIGHT', interval=1, backupCount=14) 
handler.setFormatter(logging.Formatter('%(asctime)s  %(levelname)-8s %(message)s')) 
handler.setLevel(logging.DEBUG) 
app.logger.addHandler(handler) 
app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO) 

from models.tables import User
from lib import httpagentparser
from lib import functions as f
from urlparse import urlparse

@app.before_request
def before_request():
    """Make sure we are connected to the database each request and look
    up the current user so that we know he's there.
    """
    g.redis = app.redis
    g.user = None
    if request.path.startswith('/static/'):
        return
    ua = httpagentparser.detect(request.user_agent.string)
    g.useragent = ua
    g.using_html5 = False
    if 'dist' in ua and ua['dist'].get('name', '').lower() in ['iphone', 'ipad', 'macintosh'] \
        and 'browser' in ua and ua['browser'].get('name', '').lower() in ['safari']:
        g.using_html5 = True
    if 'user_id' in session:
        g.user = f.load_user(session['user_id'])
    if g.user and 'guide_step' in g.user.extra and not request.path.startswith('/guide/') and not request.path.startswith('/m/'):
        p = None
        if request.referrer:
            parsedurl = urlparse(request.referrer)
            p = parsedurl.path
        if request.path == "/logout/":
            pass
        elif not p or not p.startswith('/guide/'):
            return redirect('/guide/')


@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    models.session.rollback()
    models.session.close()

@app.after_request
def set_cache_control(response):
    if not request.values.get('export',None):
        response.headers['Cache-Control'] = 'no-cache'
    return response

@app.template_filter()
def staticurl(s):
    return assets.versionify(s)

@app.template_filter()
def nocacheurl(s):
    return "%s?%s" % (s,''.join([choice(string.digits + string.letters) for i in range(0, 12)]),)
