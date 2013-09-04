# -*- coding: utf-8 -*-
import os
from unidecode import unidecode
import string
from random import choice
from datetime import datetime
from werkzeug import secure_filename
import pipeffmpeg
from qtfaststart import processor
from qtfaststart.exceptions import FastStartException
from flask import current_app as app
import Image

BASE60 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz23456789'

def _timebase60(d):
    return '%s%s%s%s%s%s'%(BASE60[d.year%60], BASE60[d.month-1], BASE60[d.day-1], BASE60[d.hour],
                         BASE60[d.minute], BASE60[d.second])

def _normalize(text):
    r = unidecode(unicode(text))
    return secure_filename(r)

defaultRotate={
               '90':',transpose=1',
               '180':',vflip,hflip',
               '270':',transpose=2'
               }


class VideoHelper(object):
    def __init__(self, filestream=None, savepath=None,root_path=None,rotate = '0',finalpath=None, rootdir='static/videos'):
        self.filestream = filestream
        if filestream:
            self.rawfname = _normalize(filestream.filename)
        self.root_path = app.root_path if root_path is None else root_path
        self.rootdir = os.path.join(self.root_path, rootdir)
        self.tempdir = '/tmp'
        if savepath:
            self.rawfname = os.path.basename(savepath)
            self.savepath = savepath
        else:
            self.savepath = None
        self.newmp4path = None
        self.finalpath = finalpath
        self.thumbnail = None
        self.rotate = rotate


    def save_and_process(self):
        self.save()
        try:
            self.process()
            self.cleanup()
        except:
            import traceback
            # traceback.format_exc()
            #self.cleanup()
            #self.remove()
            return False
        return True

    def read_and_process(self):
        try:
            self.process()
            self.cleanup()
        except Exception,e:
            import traceback
            # traceback.format_exc()
            #self.cleanup()
            #self.remove()
            # e
            return False
        return True


    def save(self):
        finalpath = self.get_final_path()
        self.finalpath = finalpath
        fname, ext = os.path.splitext(self.rawfname)
        finalname,noext = os.path.splitext(finalpath)
        fname = '%s_%s%s'%(finalname, ''.join([choice(string.digits) for i in range(12)]), ext)
        self.savepath = fname
        self.filestream.save(self.savepath)


    def process(self):
        if not self.savepath:
            raise Exception('video file not saved')
        fname, ext = os.path.splitext(self.savepath)
        newmp4path = '%s_%s%s'%(fname, ''.join([choice(string.digits) for i in range(3)]), '.mp4')
        self.newmp4path = newmp4path

        self.convert_tomp4()
        if not self.finalpath:
            finalpath = self.get_final_path()
            self.finalpath = finalpath
        # self.newmp4path
        # self.finalpath
        processor.process(self.newmp4path, self.finalpath, limit = 32*(1024**2))

        self.get_thumbnail()


    def get_thumbnail(self,tmp = False):
        if not self.finalpath:
            raise Exception('no video to get thumbnail')
        fname, ext = os.path.splitext(self.finalpath)
        self.thumbnail = '%s_thumbnail%s'%(fname, '.jpg')
        if tmp:
            #如果是临时截图
            pipeffmpeg.get_thumbnail(self.savepath, self.thumbnail)
            im = Image.open(self.thumbnail)
            im = im.resize((320,240))
            img = Image.new("RGB", (320,320), "#000")
            img.paste(im,(0, 40))
            img.save(self.thumbnail,'JPEG')
        else:
            pipeffmpeg.get_thumbnail(self.finalpath, self.thumbnail)


    def get_meta(self):
        if self.finalpath and os.path.exists(self.finalpath):
            return pipeffmpeg.get_info(self.finalpath)
        return {}

    def convert_tomp4(self):
        info = pipeffmpeg.get_info(self.savepath)
        w, h = 320, 240
        if 'streams' in info:
            for stream in info['streams']:
                if 'width' in stream and 'height' in stream:
                    w = int(stream['width'])
                    h = int(stream['height'])
                    break
        # 'w1:%s,h2:%s'%(w,h)
        if w > h:
            #宽度度大于高度
            h = int(h*320.0/w)
            w = 320
        else:
            #宽度小于高度
            w = int(w*320.0/h)
            h = 320
        # 'w1:%s,h2:%s'%(w,h)
        if h % 2 != 0:
            h += 1
        if w % 2 != 0:
            w += 1
        rotate = defaultRotate.get(self.rotate,'')
        pipeffmpeg.convert_to(self.savepath, self.newmp4path,
                              '-filter_complex', 'scale=%d:%d%s,overlay=10:10'%(w, h, rotate),
                              inputs = ['-i', os.path.join(self.root_path, 'static/images/videos/vself_overlay48.png')])

    def cleanup(self):
        try:
            if self.newmp4path:
                os.remove(self.newmp4path)
            if self.savepath:
                os.remove(self.savepath)
        except:
            pass

    def remove(self):
        try:
            if self.finalpath:
                os.remove(self.finalpath)
            if self.thumbnail:
                os.remove(self.thumbnail)
        except:
            pass


    def get_final_path(self):
        fname, ext = os.path.splitext(self.rawfname)
        fname = '%s_%s%s'%(fname, ''.join([choice(string.digits) for i in range(6)]), '.mp4')
        def _random_name():
            n = datetime.now()
            name1 = _timebase60(n)
            return '%s%s'%(name1, choice('123456789'))
        pname = _random_name()
        ret= os.path.join(self.rootdir, pname[0:2], pname[2:4], pname[4:5], pname[5:], fname).replace('\\', '/')
        os.makedirs(os.path.dirname(ret))
        return ret

