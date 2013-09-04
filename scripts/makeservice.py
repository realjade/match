#!/usr/bin/env python
# -*- coding: utf-8 -*-

init_template = '''#! /bin/sh
# chkconfig:   - 85 15 
# description:  %(desc)s
### BEGIN INIT INFO
# Provides:          %(provider)s
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       %(description)s
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON="%(program)s"
NAME="%(app_name)s"
DESC="%(desc)s"

#set -e

case "$1" in
  start)
        echo -n "Starting $DESC: \\n"
        for i in %(program_args)s
        do
        echo "$DAEMON" $i
        $DAEMON $i start
        done
        echo "$NAME."
        ;;
  stop)
        echo -n "Stopping $DESC: \\n"
        for i in %(program_args)s
        do
        echo "$DAEMON" $i
        $DAEMON $i stop
        done
        echo "$NAME."
        ;;
  restart)
        echo -n "Restarting $DESC: \\n"
        for i in %(program_args)s
        do
        echo "$DAEMON" $i
        $DAEMON $i restart
        done
        echo "$NAME."
        ;;
  *)
        N=/etc/init.d/$NAME
        echo "Usage: $N {start|stop|restart}" >&2
        exit 1
        ;;
esac

exit 0
'''

nginx_conf_template = '''# nginx fastcgi config template

upstream beishu8 {
    server 127.0.0.1:9005;
    server 127.0.0.1:9006;
}
 
server {
    listen 80;
    server_name www.domain.com;
    location / {
        include fastcgi_params;
        fastcgi_param PATH_INFO $fastcgi_script_name;
        fastcgi_param SCRIPT_NAME "";
        fastcgi_pass beishu8;
    }
}

'''

#print init_template

d = {'provider': 'www.beishu8.com',
     'description': '',
     'app_name': 'beishu8',
     'desc': 'beishu8',
     'program': 'python /path/to/root/vself/vself.fcgi',
     'program_args': ''
     #'program_args': '"-p 3002 -t 20" "-p 3003 -t 10"'
     }

def print_help():
    print '\n'
    print 'geninitd script usage:'
    print '\tpython geninitd.py "-p 3002 -t 20" "-p 3003 -t 10"'
    print '\tit will generate the %s script. you should copy this script to /etc/init.d/ directory'%(d['app_name'])
    print '\tand make it executable(chown +x /etc/init.d/%s)'%(d['app_name'])
    
def print_ex_help():
    print '\n'
    print 'using chkconfig command to add this script to system startup services in redhat/centos'
    print '\tchkconfig --list ：显示所有运行级系统服务的运行状态信息'
    print '\tchkconfig --add name：增加一项新的服务'
    print '\tchkconfig --del name：删除服务'
    

import sys, os
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_help()
        print_ex_help()
        print '\n'
        exit(0)
    args = sys.argv[1:]
    d["program_args"] = ' '.join(map(lambda x: '"%s"'%(x), args))
    dir = os.path.dirname(os.path.abspath(__file__))
    exec_path = os.path.abspath(os.path.join(dir, '../vself.fcgi'))
    d["program"] = '%s %s'%("python", exec_path)
    f = file(d['app_name'], 'w+')
    f.write(init_template%(d))
    f.close()
