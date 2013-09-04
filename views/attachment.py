# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request, abort, g, current_app, send_file
from lib.wrappers import login_required
from models.tables import Task
import models as m
import lib.functions as f
from lib.filehelper import FileHelper
import os
from werkzeug.datastructures import FileStorage


module = Blueprint('attachment', __name__)


@module.route('/upload/attachment/', methods=['POST'])
@login_required
def upload_attachment():
    file = request.files.get('file')
    if not file:
        name = request.args.get('name')
        file = FileStorage(request.stream, filename=name, name=name, headers=request.headers)
    if file:
        fh = FileHelper(file)
        fh.save()
        if fh.savepath:
            return f.succeed({'filepath':fh.savepath})
    return f.failed(*const.UPLOAD_FAIL)


@module.route('/attachment/delete/', methods=['POST'])
@login_required
def delete_attachment():
    filepath = request.form.get('filepath',None)
    if not filepath:
        return f.failed(*const.INVALID_PARAMS)
    os.remove(filepath)
    return f.succeed('ok')


@module.route('/fujian/<path:pathurl>', methods=['GET'])
def fujian(pathurl):
    if pathurl:
        filepath = os.path.join(current_app.root_path,pathurl)
        if os.path.isfile(filepath):
            task_id = request.args.get("task_id",None)
            task = m.session.query(Task).filter(Task.task_id== task_id).first()
            if task:
                attachmentdt = task.extra.get('attachmentdt',{})# 根据路径查询文件名是否存在
                rename = attachmentdt.get("/%s" % pathurl,None)
                if not rename:
                    rename = os.path.basename(pathurl)
                return send_file(filepath,as_attachment = True,attachment_filename=rename.encode('gb2312'))
    return abort(404)
