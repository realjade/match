# -*- coding: utf-8 -*-
from models.base import buildmixin, Base
from flask import g, json
from sqlalchemy import Table
from models import metadata, session
import time
from sqlalchemy import desc, asc


reportcard = Table('reportcard',metadata, autoload = True)

class ReportCard(Base):
    __table__ = reportcard
