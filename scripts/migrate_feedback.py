#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Creates shell
"""
from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.datastructures import CallbackDict
import json
import time

create_sqls = [
'''
CREATE TABLE `feedback` (
  `id` bigint(20) NOT NULL auto_increment,
  `email` varchar(50) ,
  `name` varchar(50),
  `content` text,
  `readed` smallint(6),
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
'''
]

config = {}
config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:111111@127.0.0.1:3306/vself?charset=utf8'
#config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://vself:vself2012@42.121.65.179:3306/vself?charset=utf8'
config['SQLALCHEMY_POOL_SIZE'] = 3
config['SQLALCHEMY_POOL_MAX_OVERFLOW'] = 3

engine = create_engine(config['SQLALCHEMY_DATABASE_URI'],
                       pool_size=config['SQLALCHEMY_POOL_SIZE'],
                       max_overflow=config['SQLALCHEMY_POOL_MAX_OVERFLOW'])
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
metadata = MetaData(bind=engine)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base(metadata=metadata)
Base.query = session.query_property()

def alter_tables(sqls):
    for sql in sqls:
        conn = engine.connect()
        try:
            conn.execute(sql)
        except:
            pass
        conn.close()
    
if __name__ == '__main__':
    alter_tables(create_sqls)