# -*- coding: utf-8 -*-
#!/usr/bin/python
import os
from fabric.api import hosts, run, env, local, cd, get, lcd

env.hosts = ["share@112.124.32.90","vself@42.121.89.234"]
env.passwords = {"share@112.124.32.90":"thepass","vself@42.121.89.234":"vself2045"}
# 179  v.beishu8.com
# 234  beishu8.com

############v.beishu8.com#############
@hosts("vself@42.121.65.179")
def update():
    """更新v.beishu8.com代码"""
    with cd("/home/vself/services/vself"):
        run("hg pull")
        run("hg update -C")
        # run("python scripts/updb130318.py") # 增加系统通知
        #run("python scripts/updb130321.py") # 修改classgrade数据库
        run("python assets.py")# 清理浏览器缓存
        

@hosts("vself@42.121.65.179")
def restart():
    """重启v.beishu8.com服务"""
    with cd("/home/vself/services/vself"):
        run("sudo celery multi restart celerytasks -A celerytasks --concurrency=2 -l info --pidfile=/var/run/%n.pid --logfile=/var/log/celery/%n.log")
        run("python vself.fcgi -t 20 -p 9005 restart")


###########线上############## 未测试
@hosts("vself@42.121.89.234")
def updateonline():
    """更新 beishu8.com 代码"""
    
    with cd("/home/vself/services/vself"):
        run("hg pull")
        run("hg update -C")
        run("python assets.py")# 清理浏览器缓存

@hosts("vself@42.121.89.234")
def restartonline():
    """停止beishu8.com服务"""
    with cd("/home/vself/services/vself"):
        # run("sudo celery multi start celerytasks -A celerytasks --concurrency=2 -l info --pidfile=/var/run/%n.pid --logfile=/var/log/celery/%n.log")
        #run("sudo celery beat --app=celerytasks -l info --pidfile=/var/run/celerytasks.pid --logfile=/var/log/celery/celerytasks.log &")
        run("./beishu8 restart")


@hosts("vself@42.121.89.234")
def startonline():
    """启动beishu8.com服务"""
    with cd("/home/vself/services/vself"):
        run("./beishu8 start")


@hosts("vself@42.121.89.234")
def stoponline():
    """停止beishu8.com服务"""
    with cd("/home/vself/services/vself"):
        run("./beishu8 stop")
