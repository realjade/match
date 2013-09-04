# -*- coding: utf-8 -*-
from alter_db import alter_tables

"""
    删除班级表中的学校 入学年份和班级
"""

create_sqls = [
'''
alter table `classgrade` drop column period;
''',
'''
alter table `classgrade` drop column classroom;
''',
'''
alter table `classgrade` drop column school_id;
''',
'''
alter table `classgrade` add school varchar(200) AFTER `class_id`;
''',
]

if __name__ == "__main__":
    alter_tables(create_sqls)
