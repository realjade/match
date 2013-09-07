# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
INSERT INTO `match`.`user` (`mobile`, `pw_hash`, `nickname`, `isadmin`, `gender`) VALUES ('18000000000', 'pbkdf2:sha1:1000$39kc5SB6$8010f2648f0f5fe767d8cbc20754a2d44d575143', 'admin', 1, 1);
''',
'''
INSERT INTO `match`.`user` (`mobile`, `pw_hash`, `nickname`, `isadmin`, `gender`) VALUES ('18000000001', 'pbkdf2:sha1:1000$39kc5SB6$8010f2648f0f5fe767d8cbc20754a2d44d575143', 'not admin', 0, 1);
''',
'''
INSERT INTO `match`.`city` (`name`) VALUES ('杭州');
''',
'''
INSERT INTO `match`.`city` (`name`) VALUES ('长沙');
''',
'''
INSERT INTO `match`.`city` (`name`) VALUES ('昆明');
''',
'''
INSERT INTO `match`.`city` (`name`) VALUES ('广州');
''',
'''
INSERT INTO `match`.`city` (`name`) VALUES ('合肥');
''',
'''
INSERT INTO `match`.`city` (`name`) VALUES ('武汉');
''',
'''
INSERT INTO `match`.`city` (`name`) VALUES ('西安');
''',
'''
INSERT INTO `match`.`city` (`name`) VALUES ('南宁');
'''
]

if __name__ == "__main__":
    alter_tables(create_sqls)
