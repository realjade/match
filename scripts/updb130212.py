# -*- coding: utf-8 -*-
from alter_db import alter_tables

create_sqls = [
'''
ALTER TABLE `video` ADD COLUMN `status` VARCHAR(10) NOT NULL DEFAULT 'finished'  AFTER `thumbnail_path`;
ALTER TABLE `reportcard` ADD COLUMN `class_id` VARCHAR(20) AFTER `reportcard_name`;
''',
]

if __name__ == "__main__":
    alter_tables(create_sqls)
