# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta
from datetime import date
import calendar
import time

def _week_start_day(_date):
    weekday = date.isocalendar(_date)
    start_date = _date - timedelta(weekday[2]-1)
    d = datetime(int(start_date.year),int(start_date.month),int(start_date.day),0,0,0,0)
    return d

def _week_end_day(_date):
    weekday = date.isocalendar(_date)
    end_date = _date + timedelta(7-weekday[2])
    d = datetime(int(end_date.year),int(end_date.month),int(end_date.day),23,59,59,999)
    return d

def _month_start_day(_date):
    return datetime(int(_date.year),int(_date.month),1,0,0,0,0)
    
def _month_end_day(_date):
    days  = calendar.monthrange(_date.year,_date.month)[1]
    return datetime(int(_date.year),int(_date.month),days,23,59,59,999)

def _week_start_stamp(_date):
    d = _week_start_day(_date)
    return time.mktime(d.timetuple())*1000
    
def _week_end_stamp(_date):
    d = _week_end_day(_date)
    return time.mktime(d.timetuple())*1000
    
def _month_start_stamp(_date):
    start_date = _date - timedelta(_date.day-1)
    d = datetime(int(start_date.year),int(start_date.month),int(start_date.day),0,0,0,0)
    return time.mktime(d.timetuple())*1000
    
def _month_end_stamp(_date):
    days = calendar.monthrange(_date.year,_date.month)[1]
    d = datetime(int(_date.year),int(_date.month),days,23,59,59,999)
    return time.mktime(d.timetuple())*1000
    
def _stamp_to_date(stamp):
    return date.fromtimestamp(stamp/1000.0)

def _begin_stamp(d):
    date = datetime(int(d.year),int(d.month),int(d.day),0,0,0,0)
    return time.mktime(date.timetuple())*1000
    
def _end_stamp(d):
    date = datetime(int(d.year),int(d.month),int(d.day),23,59,59,999)
    return time.mktime(date.timetuple())*1000

def _stamp_to_date(stamp):
    return date.fromtimestamp(stamp/1000.0)