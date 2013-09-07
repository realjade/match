# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
import time
from sqlalchemy import desc, asc
from lib import utils as ut


match = Table("match", metadata, autoload=True)


class Match(Base, buildmixin('extra')):
    __table__ = match
    
    def tojson(self):
        import lib.filters as ft
        return {'id':self.id,
                'course':self.course,
                'isstudent':self.isstudent,
                'isteacher':self.isteacher,
                'isparent':self.isparent,
                'smallavatar': ft.avatar(self),
                'mediumavatar': ft.avatar(self,'medium'),
                'bigavatar': ft.avatar(self,'big'),
                'nickname':self.nickname,
                'email':self.email,
                'mobile':self.mobile,
                }