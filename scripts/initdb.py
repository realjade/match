# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
create table `user` (
  `id` bigint(20) NOT NULL auto_increment,
  `mobile` varchar(50) not null,
  `pw_hash` varchar(100) not null,
  `nickname` varchar(50) not null,
  `isadmin` tinyint(1) not null default 0,
  `gender` tinyint(1) not null default 1 comment '0:femal,1:male',
  `area` varchar(300),
  `slogan` varchar(500),
  `avatar` varchar(300),
  `height` smallint(6),
  `weight` float,
  `team_id` varchar(20) not null default '-1',
  `role` varchar(20) comment 'player 普通球员，captain 队长、vice-captain 副队长、leader 领队、coach 教练',
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
, ADD UNIQUE INDEX `user_mobile_index` (`mobile` ASC) ;
''',
'''
create table `team` (
  `id` bigint(20) NOT NULL auto_increment,
  `school_id` bigint(20) not null,
  `name` varchar(100) not null,
  `area` varchar(300),
  `avatar` varchar(300),
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `city` (
  `id` bigint(20) NOT NULL auto_increment,
  `name` varchar(100) not null,
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `school` (
  `id` bigint(20) NOT NULL auto_increment,
  `city_id` bigint(20) not null,
  `name` varchar(100) not null,
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `school` 
ADD INDEX `city_id_index` (`city_id` ASC);
''',
'''
create table `match` (
  `id` bigint(20) NOT NULL auto_increment,
  `home_team_id` bigint(20) not null,
  `away_team_id` bigint(20) not null,
  `playingtime` bigint(20) not null,
  `playplace` varchar(20) not null comment '比赛地点，school id',
  `stage` varchar(20) not null comment '小组赛、淘汰赛、决赛、半决赛、总决赛',
  `result` varchar(20) comment '比赛结果，主客场的team id，代表输赢'，
  `mvp` varchar(20) comment 'MVP，user id',
  `scoring` varchar(20) comment '得分王，user id',
  `assists` varchar(20) comment '助攻王，user id',
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `matchresult` (
  `id` bigint(20) NOT NULL auto_increment,
  `match_id` bigint(20) not null,
  `user_id` bigint(20) not null,
  `team_id` bigint(20) not null,
  `scoring` int default 0 comment '得分',
  `penalty` int default 0 comment '罚球',
  `binaryball` int default 0 comment '二分球',
  `threepointer` int default 0 comment '三分球',
  `backboard` int default 0 comment '篮板',
  `assists` int default 0 comment '助攻',
  `steal` int default 0 comment '抢断',
  `blockshot` int default 0 comment '盖帽',
  `fault` int default 0 comment '失误',
  `foul` int default 0 comment '犯规',
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `matchresult` 
ADD UNIQUE INDEX `match_id_index` (`match_id` ASC);
''',
'''
create table `userstatistics` (
  `id` bigint(20) NOT NULL auto_increment,
  `user_id` bigint(20) not null,
  `scoring` int default 0 comment '总得分',
  `penalty` int default 0 comment '总罚球',
  `binaryball` int default 0 comment '总二分球',
  `threepointer` int default 0 comment '总三分球',
  `backboard` int default 0 comment '总篮板',
  `assists` int default 0 comment '总助攻',
  `steal` int default 0 comment '总抢断',
  `blockshot` int default 0 comment '总盖帽',
  `fault` int default 0 comment '总失误',
  `foul` int default 0 comment '总犯规',
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `userstatistics` 
ADD UNIQUE INDEX `user_id_index` (`user_id` ASC);
''',
'''
create table `teamstatistics` (
  `id` bigint(20) NOT NULL auto_increment,
  `team_id` bigint(20) not null,
  `scoring` int default 0 comment '总得分',
  `penalty` int default 0 comment '总罚球',
  `binaryball` int default 0 comment '总二分球',
  `threepointer` int default 0 comment '总三分球',
  `backboard` int default 0 comment '总篮板',
  `assists` int default 0 comment '总助攻',
  `steal` int default 0 comment '总抢断',
  `blockshot` int default 0 comment '总盖帽',
  `fault` int default 0 comment '总失误',
  `foul` int default 0 comment '总犯规',
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `teamstatistics` 
ADD UNIQUE INDEX `team_id_index` (`team_id` ASC);
''',
]

if __name__ == "__main__":
    alter_tables(create_sqls)
