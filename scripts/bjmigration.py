# -*- coding: utf-8 -*-
from werkzeug import check_password_hash, generate_password_hash
from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker
import string
import pickle
import time
from random import choice

config = {}
config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:111111@127.0.0.1:3306/vself?charset=utf8'
config['SQLALCHEMY_POOL_SIZE'] = 3
config['SQLALCHEMY_POOL_MAX_OVERFLOW'] = 3

engine = create_engine(config['SQLALCHEMY_DATABASE_URI'],
                       pool_size=config['SQLALCHEMY_POOL_SIZE'],
                       max_overflow=config['SQLALCHEMY_POOL_MAX_OVERFLOW'])
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
metadata = MetaData(bind=engine)

school              = Table("school", metadata, autoload=True)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base(metadata=metadata)
Base.query = session.query_property()

class School(Base):
    __table__ = school
    
def create_school_id():
    return ''.join([choice(string.digits + string.letters) for i in range(0,10)])
    
def get_school(path):
    readfile = open(path,'rb')
    for line in readfile:
        s = line.decode('utf-8')
        bjschool = School()
        bjschool.school_id = create_school_id()
        extra_info = {}
        arr = s.split(',')
        schoolname = arr[2]
        if schoolname.startswith(arr[0]):
            schoolname = schoolname[len(arr[0]):]
        if schoolname.startswith(arr[1]):
            schoolname = schoolname[len(arr[1]):]
        bjschool.school_name = schoolname
        bjschool.school_type = arr[6]
        bjschool.province = arr[0]
        bjschool.city = arr[0]
        bjschool.county = arr[1]
        extra_info['address'] = arr[4]
        extra_info['zip'] = arr[3]
        extra_info['phone'] = arr[5]
        print pickle.dumps(extra_info)
        bjschool.extra_f = pickle.dumps(extra_info)
        bjschool.created = time.time()*1000
        bjschool.updated = time.time()*1000
        bjschool.province = u'北京'
        bjschool.city = u'北京'
        session.add(bjschool)
        session.commit()
    readfile.close()

if __name__ == '__main__':
    get_school('./bj_schools.csv')
    get_school('./bj_middle.csv')
