# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
create table `reportcard` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id` varchar(20) not null,
  `reportcard_id` varchar(20) not null,
  `reportcard_path` varchar(300) not null,
  `reportcard_name` varchar(100) not null,
  `extra_f` blob,
  `created` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `reportcard` 
ADD INDEX `reportcard_user_id_index` (`user_id` ASC) 
, ADD UNIQUE INDEX `reportcard_reportcard_id_index` (`reportcard_id` ASC) ;
''',
]

if __name__ == "__main__":
    alter_tables(create_sqls)
