# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
ALTER TABLE `user` ADD COLUMN `is_approve` INT NULL  AFTER `is_teacher`;
''',
'''
update user set is_approve=1 where is_teacher=1;
'''
]

if __name__ == "__main__":
    alter_tables(create_sqls)
