# -*- coding: utf8 -*-
import sys,os,time
mysql_user = 'vself'
mysql_pwd = 'vself2012'
mysql_db = 'vself'
mysql_charset = 'utf8'
backup_path   = '/home/vself/services/vself/static/backup/'
cmd_path = '/usr/bin/' 
logs_path = backup_path + 'backup.log'

def writelogs(filename, contents):
    f = file(filename, 'aw')
    f.write(contents)
    f.close() # 备份目录以当日日期为名

def remove_oldbackups():
    tobe_removed = []
    for root, dirs, files in os.walk(backup_path, topdown=False):
        for fname in files:
            fpath = os.path.join(root, fname)
            if fname[0:6] == 'vself_' and fname[-3:] == '.gz':
                t = time.strptime(fname[6:-3], '%Y-%m-%d_%H:%M:%S')
                if time.time() - time.mktime(t) > 86400*5:
                    tobe_removed.append(fpath)
    for fpath in tobe_removed:
        os.remove(fpath)
        writelogs(logs_path, u'删除旧的日志文件： %s\n'%(fpath))

remove_oldbackups()

# 数据库备份名称以备份时间为名
fname = os.path.join(backup_path, time.strftime('vself_%Y-%m-%d_%H:%M:%S') + '.gz')
cmd_dump = "%smysqldump -u%s -p%s --default-character-set=%s --opt %s | gzip > %s" % \
                (cmd_path,mysql_user,mysql_pwd,mysql_charset,mysql_db,fname) # 执行备份命令
if os.system(cmd_dump) == 0:
    writelogs(logs_path,'数据备份为： ' + fname + '\n')
else:
    writelogs(logs_path,'数据备份失败！\n')
