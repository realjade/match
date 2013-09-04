# -*- coding: utf-8 -*-
import os
from unidecode import unidecode
import string
from random import choice
from datetime import datetime
from werkzeug import secure_filename
from flask import current_app as app
import Image

BASE60 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz23456789'

def _timebase60(d):
    return '%s%s%s%s%s%s'%(BASE60[d.year%60], BASE60[d.month-1], BASE60[d.day-1], BASE60[d.hour],
                         BASE60[d.minute], BASE60[d.second])

def _normalize(text):
    r = unicode(text)
    newname = secure_filename(r)
    if "." in newname:
        return newname
    else:
        return '%s.%s' % (''.join([choice(string.digits) for i in range(5)]),newname)
    


class FileHelper(object):
    def __init__(self, filestream=None, savepath=None, rootdir='static/attachment'):
        self.filestream = filestream
        if filestream:
            self.rawfname = _normalize(filestream.filename)
        else:
            self.rawfname = os.path.basename(savepath)
        self.rootdir = os.path.join(app.root_path, rootdir)
        self.tempdir = '/tmp'
        self.finalpath = None
        self.savepath = savepath


    def save(self):
        fname, ext = os.path.splitext(self.rawfname)
        fname = '%s%s'%(''.join([choice(string.digits) for i in range(12)]), ext)
        if not os.path.isfile(os.path.join(self.tempdir, fname)):
            self.savepath = os.path.join(self.tempdir, fname)
            self.filestream.save(self.savepath)

    def move(self):
        self.finalpath = self.get_final_path()
        os.rename(self.savepath, self.finalpath)
    
    def thumbnail(self,width=80,height=60):
        #生成缩略图
        fname, ext = os.path.splitext(self.finalpath)
        path,fname = os.path.split(self.finalpath)
        fname = os.path.join(path,"thumbnail%s" % ext)
        fp = Image.open(self.finalpath)
        fp.resize((width,height),Image.ANTIALIAS).save(fname)
        return "/static%s" % fname.split("vself/static")[-1]
        

    def get_final_path(self):
        fname = self.rawfname
        def _random_name():
            n = datetime.now()
            name1 = _timebase60(n)
            return '%s%s'%(name1, choice('123456789'))
        pname = _random_name()
        randomdir = ''.join([choice(string.digits) for i in range(6)])
        ret= os.path.join(self.rootdir, pname[0:2], pname[2:4], pname[4:5], pname[5:], randomdir, fname).replace('\\', '/')
        os.makedirs(os.path.dirname(ret))
        return ret

