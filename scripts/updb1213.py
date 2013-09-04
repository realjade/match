# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
create table `favimgcreate` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id` varchar(20) not null,
  `name` varchar(50) not null,
  `path` varchar(300) not null,
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `favimg` (
  `id` bigint(20) NOT NULL auto_increment,
  `favimg_id` varchar(20) not null,
  `user_id` varchar(20) not null,
  `name` varchar(50) not null,
  `reason` varchar(50) not null,
  `reply` smallint(6) not null default 0,
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `favimguser` (
  `id` bigint(20) NOT NULL auto_increment,
  `favimg_id` varchar(20) not null,
  `user_id` varchar(20) not null,
  `class_id` varchar(20) not null,
  `is_read` smallint(6) not null default 0,
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `favimgbox` (
  `id` bigint(20) NOT NULL auto_increment,
  `favimg_id` varchar(20) not null,
  `class_id` varchar(20) not null,
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `favimgitem` (
  `id` bigint(20) NOT NULL auto_increment,
  `favimg_id` varchar(20) not null,
  `user_id` varchar(20) not null,
  `name` varchar(50) not null,
  `path` varchar(300) not null,
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `favimg_comment` (
  `id` bigint(20) NOT NULL auto_increment,
  `favimg_id` varchar(20) not null,
  `user_id` varchar(20) not null,
  `comment` text not null,
  `reply_id` varchar(20),
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
]

if __name__ == "__main__":
    alter_tables(create_sqls)
