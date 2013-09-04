# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
ALTER TABLE `classgrade` ADD COLUMN `email` VARCHAR(50) NOT NULL DEFAULT ''  AFTER `school_id`;
''',
]

if __name__ == "__main__":
    alter_tables(create_sqls)
