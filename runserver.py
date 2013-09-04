# -*- coding: utf-8 -*-
import sys
from vself import app

parm = sys.argv
port = 9000

if '-p' in parm:
    try:
        port = int(parm[parm.index('-p')+1])
    except IndexError:
        print "parameter error. for example:runserver -p 80"


app.run(host="0.0.0.0", port=port)
