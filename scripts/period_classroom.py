# -*- coding: utf-8 -*-
from engine_script import session
from models.tables import Classgrade

"""
    处理线上数据库没有period和classroom信息 可循环执行
    如果出错可能是class_dt的key不全所致
"""

grade_dt = {}
grade_dt[u"初一"] = 2012
grade_dt[u"初二"] = 2011
grade_dt[u"初三"] = 2010
grade_dt[u"一"] = 2012
grade_dt[u"二"] = 2011
grade_dt[u"三"] = 2010
grade_dt[u"四"] = 2009
grade_dt[u"五"] = 2008
grade_dt[u"六"] = 2007

class_dt = {}
class_dt[u"1"] = 1
class_dt[u"一"] = 1
class_dt[u"二"] = 2
class_dt[u"三"] = 3
class_dt[u"四"] = 4
class_dt[u"五"] = 5
class_dt[u"六"] = 6
class_dt[u"七"] = 7
class_dt[u"八"] = 8


if __name__ == "__main__":
    classgrades = session.query(Classgrade).all()
    for classgrade in classgrades:
        classname = classgrade.class_name
        if u"年级" in classname:
            grade, cname = classname.split(u"年级")
            period,classroom = grade_dt[grade],class_dt[cname[0]]
        else:
            if u"届" in classname:
                period,classroom = classname[:4],class_dt[classname[5]]
            else:
                period,classroom = classname[:4],classname[4:6]
        
        classgrade.period = int(period)
        classgrade.classroom = int(classroom)
        
        print classname,period,classroom
        
    session.commit()
