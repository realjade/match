# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

# 全局的数据库引擎对象实例
engine = None
# 全局的数据库会话对象实例，如果不为 None，这应该是一个 ScopedSession
session = None
metadata = None


def setup(app):
    """创建数据库引擎对象"""
    global engine, session, metadata
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], 
                           pool_size=app.config['SQLALCHEMY_POOL_SIZE'],
                           max_overflow=app.config['SQLALCHEMY_POOL_MAX_OVERFLOW'],
                           pool_recycle = 7200)
    session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine))
    metadata = MetaData(bind=engine)