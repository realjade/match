'''
create table `competition` (
  `id` bigint(20) NOT NULL auto_increment,
  `competition_id` varchar(20) not null,
  `theme` varchar(200) not null,
  `description` varchar(500),
  `stage` varchar(20) not null comment '小组赛、淘汰赛、决赛、半决赛、总决赛',
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `competition` 
ADD UNIQUE INDEX `competition_id_index` (`competition_id` ASC);
''',
'''
create table `competitionteam` (
  `id` bigint(20) NOT NULL auto_increment,
  `competition_id` varchar(20) not null,
  `team_id` varchar(20) not null,
  `extra_f` blob,
  `created` bigint(20),
  `updated` bigint(20),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
ALTER TABLE `competitionteam`
ADD INDEX `competition_id_index` (`competition_id` ASC)
ADD INDEX `team_id_index` (`team_id` ASC);
''',