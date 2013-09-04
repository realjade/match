# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from sqlalchemy import Table
from models import metadata, session


admin = Table("admin",metadata, autoload = True)
notice = Table("notice",metadata, autoload = True)
usernotice = Table("usernotice",metadata, autoload = True)


class Admin(Base):
    __table__ = admin
    
    @property
    def user(self):
        from lib.functions import load_user
        return load_user(self.user_id)


class Notice(Base):
    __table__ = notice


class UserNotice(Base):
    __table__ = usernotice


