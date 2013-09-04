# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
ALTER TABLE `teacher_favor` ADD COLUMN `reply` INT NOT NULL DEFAULT 0  AFTER `works_id`;
ALTER TABLE `teacher_favor` ADD COLUMN `love` INT NOT NULL DEFAULT 0 AFTER `works_id`;
ALTER TABLE `teacher_favor` ADD COLUMN `click` INT NOT NULL DEFAULT 0 AFTER `works_id`;
''',

'''
create table `teacher_favor_love` (
  `id` bigint(20) NOT NULL auto_increment,
  `works_id` varchar(20) not null,
  `user_id` varchar(20) not null,
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `teacher_favor_comment` (
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
'''
create table `teacher_video` (
  `id` bigint(20) NOT NULL auto_increment,
  `video_id` varchar(20) not null,
  `user_id` varchar(20) not null,
  `class_id` varchar(20) not null,
  `favor` smallint(6) not null default 1,
  `click` smallint(6) not null default 0,
  `love` smallint(6) not null default 0,
  `reply` smallint(6) not null default 0,
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `teacher_video_comment` (
  `id` bigint(20) NOT NULL auto_increment,
  `video_id` varchar(20) not null,
  `user_id` varchar(20) not null,
  `comment` text not null,
  `reply_id` varchar(20),
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
alter table teacher_favor_love change user user_id varchar(20) not null;
''',
'''
alter table teacher_favor_comment change user user_id varchar(20) not null;
''',
'''
alter table teacher_video change user user_id varchar(20) not null;
''',
'''
alter table teacher_video_comment change user user_id varchar(20) not null;
''',
]

if __name__ == "__main__":
    alter_tables(create_sqls)
