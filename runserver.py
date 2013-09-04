# -*- coding: utf-8 -*-
import sys
from match import app

parm = sys.argv
port = 7777

if '-p' in parm:
    try:
        port = int(parm[parm.index('-p')+1])
    except IndexError:
        print "parameter error. for example:runserver -p 80"


app.run(host="0.0.0.0", port=port)
