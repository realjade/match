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
create table `passwordreset` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id` varchar(20) not null,
  `code` varchar(10),
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `passwordreset` 
ADD INDEX `resetpassword_user_id_index` (`user_id` ASC);
''',
'''
create table `demand` (
  `id` bigint(20) NOT NULL auto_increment,
  `demand_id` varchar(20) not null,
  `creator` varchar(20) not null,
  `name` varchar(100),
  `content` text,
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `demand` 
ADD INDEX `demand_demand_id_index` (`demand_id` ASC)
, ADD INDEX `demand_creator_index` (`creator` ASC) ;
''',
'''
create table `classgrade_demand` (
  `id` bigint(20) NOT NULL auto_increment,
  `demand_id` varchar(20) not null,
  `class_id` varchar(20) not null,
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `classgrade_demand` 
ADD INDEX `classgrade_demand_demand_id_index` (`demand_id` ASC)
, ADD INDEX `classgrade_demand_class_id_index` (`class_id` ASC) ;
''',
'''
alter table `works` Add column redo int not null default 0 AFTER `star`;
''',
'''
ALTER TABLE `classgrade` ADD COLUMN `period` INT NULL  AFTER `class_name` , ADD COLUMN `classroom` INT NULL  AFTER `period` ;

'''
]

config = {}
config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:111111@127.0.0.1:3306/vselfonline?charset=utf8'
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
