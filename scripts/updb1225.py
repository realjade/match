# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
create table `ireadcount` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id` varchar(20) not null,
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
]

if __name__ == "__main__":
    alter_tables(create_sqls)
