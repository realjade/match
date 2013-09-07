# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
from sqlalchemy import desc, asc


team = Table("team", metadata, autoload=True)
city = Table("city", metadata, autoload=True)
school = Table("school", metadata, autoload=True)

class Team(Base, buildmixin('extra')):
    __table__ = team
    
    @property
    def school(self):
        return session.query(School).filter(School.id == self.school_id).first()
    
    def tojson(self):
        return {'id':self.id,
                'school_id':self.school_id,
                'school':self.school.tojson(),
                'name':self.name,
                'logo':self.logo,
                }

class City(Base, buildmixin('extra')):
    __table__ = city
    
    def tojson(self):
        return {'id':self.id,
                'name':self.name,
                }
        
class School(Base, buildmixin('extra')):
    __table__ = school
    
    @property
    def city(self):
        return session.query(City).filter(City.id == self.city_id).first()
    
    def tojson(self):
        return {'id':self.id,
                'name':self.name,
                'city':self.city.tojson()
                }