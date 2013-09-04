# -*- coding: utf-8 -*-
from alter_db import alter_tables

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

if __name__ == "__main__":
    alter_tables(create_sqls)
