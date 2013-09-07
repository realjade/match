# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
INSERT INTO `match`.`user` (`mobile`, `pw_hash`, `nickname`, `isadmin`, `gender`) VALUES ('18000000000', 'pbkdf2:sha1:1000$39kc5SB6$8010f2648f0f5fe767d8cbc20754a2d44d575143', 'admin', 1, 1);
'''
]

if __name__ == "__main__":
    alter_tables(create_sqls)
