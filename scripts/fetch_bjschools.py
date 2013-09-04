# -*- coding: utf-8 -*-
import urllib, urllib2
from urllib2 import Request, urlopen
from werkzeug.urls import url_encode
from lxml import etree

url = 'http://www.beijingmap.gov.cn/bjjw/BJMapSearch'
params = {'l':'bjjw_ptxx','s':u'10,0,东城区)*','p':'0,10','t':'xml'}
middleparams = {'l':'bjjw_ptzx','s':u'3,0,东城区)*','p':'0,10','t':'xml'}


def http_get(url, params={}, encoding='utf-8'):
    encoded_params = url_encode(params)
    
    if len(encoded_params) > 0:
        url += '?' + encoded_params
    req = Request(url)
    print 'start get %s'%(url)
    
    try:
        f = urlopen(req, timeout = 60)
        r = f.read()
        f.close()
        return r
    except urllib2.URLError, e:
        print 'failed: %s'%(e)
        return None
    except Exception,e:
        print 'failed: %s'%(e)
        return None

def handle_fetch(data):
    if not data:
        return (0,[])
    total = 0
    ret = []
    print data
    response = etree.fromstring(data)
    response = list(response)
    total = int(response[1].text)
    hts = list(response[3])[0]
    for ht in hts:
        school= {'name':ht.get(u'学校名称'),'address':ht.get(u'地址'),
                 'zip': ht.get(u'邮编'),'belong':ht.get(u'所属区县'),
                 'phone':ht.get(u'电话')}
        ret.append(school)
    return (total,ret)



def fetch_one(**kwargs):
    p = dict(params)
    p.update(kwargs)
    return handle_fetch(http_get(url, p))

def start_fetch():
    fetch_one()

def fetch_all():
    savefile = open('./bj_schools.csv','a+')
    for dis in district:
        d = dict({'s':u'10,0,%s)*'%district.get(dis)})
        data = fetch_one(**d)
        count = len(data[1])
        for school in data[1]:
            savefile.write('%s,%s,%s,%s,%s,%s,%s\r\n'%(u'北京市',school['belong'],school['name'],school['zip'],school['address'],school['phone'],'PRIMARY'))
        while count < data[0]:
            d = dict({'s':u'10,0,%s)*'%district.get(dis),'p':'%d,%d'%(count,count+10)})
            data = fetch_one(**d)
            count += len(data[1])
            for school in data[1]:
                savefile.write('%s,%s,%s,%s,%s,%s,%s\r\n'%(u'北京市',school['belong'],school['name'],school['zip'],school['address'],school['phone'],'PRIMARY'))
    savefile.close()
    
def fetch_middle(**kwargs):
    p = dict(middleparams)
    p.update(kwargs)
    return handle_fetch(http_get(url,p))

def get_middle_school():
    savefile=open('./bj_middle.csv','a+')
    for dis in district:
        d = dict({'s':u'3,0,%s)*'%district.get(dis)})
        data = fetch_middle(**d)
        count = len(data[1])
        for school in data[1]:
            savefile.write('%s,%s,%s,%s,%s,%s,%s\r\n'%(u'北京市',school['belong'],school['name'],school['zip'],school['address'],school['phone'],'MIDDLE'))
        while count < data[0]:
            d = dict({'s':u'3,0,%s)*'%district.get(dis),'p':'%d,%d'%(count,count+10)})
            data = fetch_middle(**d)
            count += len(data[1])
            for school in data[1]:
                savefile.write('%s,%s,%s,%s,%s,%s,%s\r\n'%(u'北京市',school['belong'],school['name'],school['zip'],school['address'],school['phone'],'MIDDLE'))
    savefile.close()


def get_school(data):
    result = []
    for d in data:
        spaceindex = d[1].rfind(' ')
        numindex = d[1].rfind(u'个')
        n = int(d[1][spaceindex+1:numindex])
        if n > 0:
            result.append(d[0])
    return result
    
bj_setting = [('1',['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19'])]
district = {'1':u'东城区','2':u'西城区','3':u'崇文区',
            '4':u'宣武区','5':u'朝阳区','6':u'丰台区',
            '7':u'石景山区','8':u'海淀区','9':u'门头沟区',
            '10':u'房山区','11':u'通州区','12':u'顺义区',
            '13':u'延庆县','14':u'昌平区','15':u'怀柔区',
            '16':u'密云县','17':u'平谷区','18':u'大兴区',
            '19':u'其他地区'}
province = {'1':u'北京市'}


if __name__ == '__main__':
    #start_fetch()
    fetch_all()
    #get_middle_school()
