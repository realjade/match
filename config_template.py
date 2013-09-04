# -*- coding: utf-8 -*-

# configuration
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'
# 数据库连接配置
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://vself:vself2012@localhost:3306/vself?charset=utf8'

# 数据库连接池最大连接数
SQLALCHEMY_POOL_SIZE = 45

# 数据库连接池最大允许过载数
SQLALCHEMY_POOL_MAX_OVERFLOW = 45

LOG_PATH = 'logs'

#RPC host
RPCHOST = 'http://127.0.0.1:9000'

REDIS_HOST = '192.168.64.98'
REDIS_PORT = 9999
REDIS_DB   = 0
REDIS_PASSWORD = None

RECORD_ROOT = 'static/record/videos'
RECORD_HOST = '127.0.0.1:1935'

#邮件发送配置
SMTP_SENDER='noreply@beishu8.com'
SMTP_SERVER='smtp.exmail.qq.com'
SMTP_SENDER_PASSWORD = 'vself2012'
FROM_EMAIL='noreply@beishu8.com'
SENDER_NICKNAME=u'背书吧'