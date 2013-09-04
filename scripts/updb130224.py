# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
create table `teacher_favorimg` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id` varchar(20) not null,
  `class_id` varchar(20) not null,
  `task_id` varchar(20) not null,
  `works_id` varchar(20) not null,
  `click` smallint(6) not null default 0,
  `love` smallint(6) not null default 0,
  `reply` smallint(6) not null default 0,
  `created` bigint(20),
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `teacher_favorimg_love` (
  `id` bigint(20) NOT NULL auto_increment,
  `works_id` varchar(20) not null,
  `user_id` varchar(20) not null,
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `teacher_favorimg_comment` (
  `id` bigint(20) NOT NULL auto_increment,
  `works_id` varchar(20) not null,
  `user_id` varchar(20) not null,
  `comment` text,
  `reply_id` varchar(20),
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
]

if __name__ == "__main__":
    alter_tables(create_sqls)
