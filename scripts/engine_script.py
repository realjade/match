# -*- coding: utf-8 -*-
from os.path import abspath, dirname, join
import sys
sys.path.insert(0, abspath(join(abspath(dirname(__file__)), '..')))

from flask import Flask
import config
app = Flask(__name__)
app.config.from_object(config)
import models
models.setup(app)

from models import session

__all__ = ["session",]
"""
    目的:专门用于使用sqlalchemy处理数据
    使用方法:
        1.当前目录下 新建脚本文件 xxx.py
        2.导入 from engine_script import session
        3.再导入相关models对象操作
"""
