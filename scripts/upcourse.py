# -*- coding: utf-8 -*-
from engine_script import session
from models.tables import User

"""
    更新教师的 课程 列表到字符串格式
"""

if __name__ == "__main__":
    users = session.query(User).all()
    for user in users:
        course = user.extra.get("course",None)
        
        if isinstance(course,list):
            print course,type(course)
            user.extra["course"] = course[0]
        elif course == None:
            print course,type(course),unicode
            user.extra["course"] = u"语文"
        else:
            print course
    
    session.commit()
