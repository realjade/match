# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
import time
from sqlalchemy import desc, asc


school = Table("school",metadata,autoload=True)


class School(Base):
    __table__ = school
    
    def __str__(self):
        return self.fullname
    
    @property
    def classgrades(self):
        from models.classgrade import Classgrade
        classgrades = session.query(Classgrade).filter(self.school_id == Classgrade.school_id).all()
        return classgrades

    @property
    def fullname(self,devide=' > '):
        return self.province+devide+self.city+devide+self.county+devide+self.school_name
