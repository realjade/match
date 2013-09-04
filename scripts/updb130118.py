# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
create table `multitask` (
  `id` bigint(20) NOT NULL auto_increment,
  `multitask_id` varchar(20) not null,
  `user_id` varchar(20) not null,
  `task_type` smallint(6) not null,
  `task_content` varchar(500) not null,
  `class_ids` varchar(500) not null,
  `starttime` bigint(20) not null,
  `endtime` bigint(20) not null,
  `rate` smallint(6) not null,
  `current` smallint(6) not null,
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `multitask` 
ADD INDEX `multitask_user_id_index` (`user_id` ASC) 
, ADD UNIQUE INDEX `multitask_multitask_id_index` (`multitask_id` ASC) ;
''',
'''
ALTER TABLE `task` ADD COLUMN `ismulti` smallint(6) default 0  AFTER `task_type` ;
'''
]

if __name__ == "__main__":
    alter_tables(create_sqls)
