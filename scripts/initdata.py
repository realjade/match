# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
create table `user` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id` varchar(20) not null,
  `mobile` varchar(50) not null,,
  `pw_hash` varchar(100) not null,
  `nickname` varchar(50) not null,
  `isadmin` tinyint(1) not null default 0,
  `isplayer` tinyint(1) not null,
  `role` varchar(20) comment '队长、副队长、领队、教练',
  `gender` tinyint(1) not null default 1 comment '0:femal,1:male',
  `address` varchar(300),
  `slogan` varchar(500),
  `avatar` varchar(300),
  `height` smallint(6),
  `weight` smallint(6),
  `position` varchar(20) comment '大前锋、小前锋、中锋、得分后卫、控球后卫',
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `user` 
ADD UNIQUE INDEX `user_id_index` (`user_id` ASC)
, ADD INDEX `user_mobile_index` (`mobile` ASC) ;
''',
]

if __name__ == "__main__":
    alter_tables(create_sqls)
