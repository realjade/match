#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Creates shell
"""
from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.datastructures import CallbackDict
import json

create_sqls = [
'''
create table `user` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id` varchar(20) not null,
  `nickname` varchar(50) not null,
  `email` varchar(50),
  `mobile` varchar(50),
  `pw_hash` varchar(100) not null,
  `is_teacher` smallint(6) default 0,
  `is_student` smallint(6) default 0,
  `is_parent` smallint(6) default 0,
  `is_partner` smallint(6) default 0,
  `partner_info` varchar(30),
  `avatar` varchar(300),
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `user` 
ADD UNIQUE INDEX `user_id_index` (`user_id` ASC) 
, ADD INDEX `user_email_index` (`email` ASC) 
, ADD INDEX `user_mobile_index` (`mobile` ASC) ;
''',
'''
create table `user_classgrade` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id` varchar(20) not null,
  `class_id` varchar(20) not null,
  `identity` smallint(6) default 0,
  `course` varchar(20),
  `is_creator` smallint(6) default 0,
  `valid` smallint(6) default 1,
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `user_classgrade` 
ADD INDEX `user_classgrade_user_id_index` (`user_id` ASC) 
, ADD INDEX `user_classgrade_class_id_index` (`class_id` ASC) ;
''',
'''
create table `admin`(
    `id` bigint(20) auto_increment NOT NULL,
    `admin_id` varchar(20) not null,
    `user_id` varchar(20) not null,
    `extra_f` blob,
    `created` bigint(20),
    `updated` bigint(20),
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `admin` 
ADD UNIQUE INDEX `admin_admin_id_index` (`admin_id` ASC) 
, ADD INDEX `admin_user_id_index` (`user_id` ASC) ;
''',
'''
CREATE TABLE `classgrade` (
  `id` bigint(20) auto_increment NOT NULL,
  `class_id` varchar(20) not null,
  `class_name` varchar(200) not null,
  `school_id` varchar(20) not null, 
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20), 
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `classgrade` 
ADD UNIQUE INDEX `classgrade_class_id_index` (`class_id` ASC) 
, ADD INDEX `classgrade_school_id_index` (`school_id` ASC) ;
''',
'''
CREATE TABLE `school` (
  `id` bigint(20) auto_increment  NOT NULL , 
  `school_id` varchar(20) NOT NULL , 
  `province` varchar(20) NOT NULL , 
  `city` varchar(30) NOT NULL , 
  `county` varchar(20) NOT NULL ,
  `school_name` varchar(50) NOT NULL , 
  `school_type` varchar(30), 
  `extra_f` blob, 
  `created` bigint(20), 
  `updated` bigint(20),
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `school` 
ADD UNIQUE INDEX `school_school_id_index` (`school_id` ASC);
''',
'''
create table `task` (
  `id` bigint(20) NOT NULL auto_increment,
  `task_id` varchar(20) not null,
  `task_content` varchar(500) not null,
  `task_type` smallint(6) not null,
  `creator` varchar(20) not null,
  `need_approval` smallint(6),
  `dead_line` bigint(20),
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `task` 
ADD UNIQUE INDEX `task_task_id_index` (`task_id` ASC) 
, ADD INDEX `task_creator_index` (`creator` ASC) ;
''',
'''
create table `classgrade_task` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id`  varchar(20) not null,
  `class_id` varchar(20) not null,
  `task_id` varchar(20) not null,
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `classgrade_task` 
ADD INDEX `classgrade_task_user_id_index` (`user_id` ASC) 
, ADD INDEX `classgrade_task_class_id_index` (`class_id` ASC) 
, ADD INDEX `classgrade_task_task_id_index` (`task_id` ASC) ;
''',
'''
create table `video` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id` varchar(20) not null,
  `video_id` varchar(20) not null,
  `video_path` varchar(300) not null,
  `thumbnail_path` varchar(300) not null,
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `video` 
ADD INDEX `video_user_id_index` (`user_id` ASC) 
, ADD UNIQUE INDEX `video_video_id_index` (`video_id` ASC) ;
''',
'''
create table `index_video` (
  `id` bigint(20) NOT NULL auto_increment,
  `works_id` varchar(20) not null,
  `video_id` varchar(20) not null,
  `task_id` varchar(20) not null,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `index_video` 
ADD INDEX `index_video_works_id_index` (`works_id` ASC) 
, ADD INDEX `index_video_video_id_index` (`video_id` ASC) 
, ADD INDEX `index_video_task_id_index` (`task_id` ASC) ;
''',
'''
create table `taskbox` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id` varchar(20) not null,
  `task_id` varchar(20) not null,
  `class_id` varchar(20),
  `works_id` varchar(20),
  `confirm` smallint(6),
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `taskbox` 
ADD INDEX `taskbox_user_id_index` (`user_id` ASC) 
, ADD INDEX `taskbox_task_id_index` (`task_id` ASC) 
, ADD INDEX `taskbox_class_id_index` (`class_id` ASC) 
, ADD INDEX `taskbox_works_id_index` (`works_id` ASC) ;
''',
'''
create table `works` (
  `id` bigint(20) NOT NULL auto_increment,
  `works_id` varchar(20) not null,
  `user_id` varchar(20) not null,
  `content_f` blob,
  `teacher_readed` smallint(6),
  `teacher_comment` text,
  `parent_approval` smallint(6),
  `parent_comment` text,
  `star` float,
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY(`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `works` 
ADD UNIQUE INDEX `works_works_id_index` (`works_id` ASC) 
, ADD INDEX `works_user_id_index` (`user_id` ASC) ;
''',
'''
create table `teacher_favor` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id` varchar(20) not null,
  `class_id` varchar(20) not null,
  `task_id` varchar(20) not null,
  `works_id` varchar(20) not null,
  `created` bigint(20),
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `teacher_favor` 
ADD INDEX `teacher_favor_class_id_index` (`class_id` ASC) 
, ADD INDEX `teacher_favor_works_id_index` (`works_id` ASC) ;
''',
'''
create table `timeline` (
  `id` bigint(20) NOT NULL auto_increment,
  `event` varchar(50) not null,
  `user_id` varchar(20) not null,
  `class_id` varchar(20),
  `to_user_id` varchar(20),
  `task_id` varchar(20),
  `works_id` varchar(20),
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY(`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `timeline` 
ADD INDEX `timeline_event_index` (`event` ASC) 
, ADD INDEX `timeline_user_id_index` (`user_id` ASC) 
, ADD INDEX `timeline_to_user_id_index` (`to_user_id` ASC) 
, ADD INDEX `timeline_task_id_index` (`task_id` ASC) ;
''',
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
''',
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
]

# 作业重做 修改表结构 alter table `works` Add column redo int not null default 0 AFTER `star`

'''
timeline:
  event: class.create,  class.join,  task.publish, task.compelete, works.star, works.teacher.comment, works.approval, works.parent.comment
'''
config = {}
config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:111111@localhost:3306/vself?unix_socket=/tmp/mysql.sock&charset=utf8'
#config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:111111@localhost:3306/vself?unix_socket=/var/run/mysqld/mysqld.sock&charset=utf8'
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

def init_tables(sqls):
    for sql in sqls:
        conn = engine.connect()
        try:
            conn.execute(sql)
        except:
            pass
        conn.close()

    
if __name__ == '__main__':
    init_tables(create_sqls)
    
#修改记录
modifylog=(
           
           )
