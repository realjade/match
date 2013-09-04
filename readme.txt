sudo celery multi start celerytasks -A celerytasks --concurrency=2 -l info --pidfile=/var/run/%n.pid --logfile=/var/log/celery/%n.log
celery worker --app=celerytasks -l info --concurrency=1

sudo celery beat --app=celerytasks -l info --pidfile=/var/run/celerybeat/celerytasks.pid --logfile=/var/log/celery/celerybeat/celerytasks.log &