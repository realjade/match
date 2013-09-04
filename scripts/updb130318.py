# -*- coding: utf-8 -*-
from alter_db import alter_tables

"""
    系统通知notice 根据注册时间查询自己的通知信息
        content
        creator
        
    是否已读（通知默认不写入）
        notice_id
        isread
    
    # 站内信设计 未加
        记录id
        发件人
        收件人 accept_user
        标题
        内容
        时间
        回复_记录id
        是否读取
"""

create_sqls = [
'''
create table `notice` (
  `id` bigint(20) NOT NULL auto_increment,
  `notice_id` varchar(20) not null,
  `content` varchar(500) not null,
  `creator` varchar(20) not null,
  `created` bigint(20),
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
'''
create table `usernotice` (
  `id` bigint(20) NOT NULL auto_increment,
  `notice_id` varchar(20) not null,
  `accept_user` varchar(20) not null,
  `isread` smallint(6) not null default 0,
  `created` bigint(20),
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
''',
]

if __name__ == "__main__":
    alter_tables(create_sqls)
