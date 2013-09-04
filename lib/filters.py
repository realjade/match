# -*- coding: utf-8 -*-
from datetime import datetime
import time
import types
import pystache
from flask import current_app, json, request
from jinja2 import evalcontextfilter, Markup, contextfunction, Environment
import os

def format_datetime(value, format='medium'):
    if not value:
        return ''
    if format == 'full':
        format=u"%Y年%m月%d日, %H:%M:%S"
    elif format == 'medium':
        format=u"%m月%d日%H:%M"
    elif format == 'date':
        format=u"%Y年%m月%d日"
    if type(value) in [types.IntType, types.LongType, types.FloatType]:
        value = datetime.fromtimestamp(int(value)/1000)
    return value.strftime(format.encode('utf-8')).decode('utf-8')


def slist(data):
    if type(data) not in [types.ListType, types.TupleType]:
        return [data]
    else:
        return data


def ifdefault(value,expression,default = ''):
    return value if expression else default


@contextfunction
def render_mustache(context, template_path, **kwargs):
    env = Environment(loader=context.environment.loader, trim_blocks=True)
    env.variable_start_string = '{{{{'
    env.variable_end_string = '}}}}'
    env.comment_start_string = '{{{#'
    env.comment_end_string = '#}}}'
    #loader = env.loader
    #template, filename, uptodate= loader.get_source(env, template_path)
    template_context = dict(context.get_all())
    template_context.update(**kwargs)
    template = env.get_template(template_path, globals=template_context)
    template = template.render()
    view = dict(context.get_all())
    view.update(**kwargs)
    result = pystache.render(template, view)
    if context.eval_ctx.autoescape:
        result = Markup(result)
    return result


@contextfunction
def include_mustache(context, template_path, scriptag=True, **kwargs):
    env = Environment(loader=context.environment.loader, trim_blocks=True)
    env.variable_start_string = '{{{{'
    env.variable_end_string = '}}}}'
    env.comment_start_string = '{{{#'
    env.comment_end_string = '#}}}'
    #loader = env.loader
    #template, filename, uptodate= loader.get_source(env, template_path)
    template_context = dict(context.get_all())
    template_context.update(**kwargs)
    template = env.get_template(template_path, globals=template_context)
    template = template.render()
    stagid = os.path.splitext(template_path)[0].replace('/', '_')
    if scriptag:
        template = '<script id="%s" class="mustache-template" type="text/template">\n%s\n</script>'%(stagid, template)
    if context.eval_ctx.autoescape:
        template = Markup(template)
    return template


@contextfunction
def get_context(context):
    return context


def avatar(user, size='small'):
    if not user.avatar:
        return '/static/images/icons/avatar.jpg'
    fname = '50.jpg'
    if size == 'medium':
        fname = '100.jpg'
    if size == 'big':
        fname = '150.jpg'
    return '%s/%s?ver=%s'%(user.avatar, fname,int(time.time()))


def gettext(user):
    if isinstance(user,dict):
        if user["isparent"]:
            return u'家长'
        elif user["isteacher"]:
            return u'老师'
        elif user["isstudent"]:
            return u'学生'
        else:
            return u""
    else:
        if user.isparent:
            return u'家长'
        elif user.isteacher:
            return u'老师'
        elif user.isstudent:
            return u'学生'
        else:
            return u''

def fullinfo(user):
    if user is None:
        return json.dumps({})
    return json.dumps(user.tojson())

def revise_name(name,length = 19):
    name = name.encode("gb18030")
    if len(name) > length:
        try:
            name = name[:length].decode("gb18030")
        except UnicodeDecodeError:
            name = name[:length-1].decode("gb18030")
        return u"%s..." % name
    return name.decode("gb18030")



def setup(app):
    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['slist'] = slist
    app.jinja_env.filters['ifdefault'] = ifdefault
    app.jinja_env.globals['render_mustache'] = render_mustache
    app.jinja_env.globals['include_mustache'] = include_mustache
    app.jinja_env.globals['context'] = get_context
    app.jinja_env.filters['avatar'] = avatar
    app.jinja_env.filters['revise_name'] = revise_name
    app.jinja_env.filters['gettext'] = gettext
    app.jinja_env.filters['fullinfo'] = fullinfo
