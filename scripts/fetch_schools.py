# -*- coding: utf-8 -*-
import urllib, urllib2
from urllib2 import Request, urlopen
from werkzeug.urls import url_encode
import lxml.html

url = 'http://class.chinaren.com/search.do'
params = {'keyword':'', 'leveltype':0, 'searchtype':1, 'provid':1, 'area':1, 'schooltype':1}


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
        return r.decode(encoding)
    except urllib2.URLError, e:
        print 'failed: %s'%(e)
        return None
    except Exception,e:
        print 'failed: %s'%(e)
        return None

def handle_fetch(data):
	if not data:
		return
	h = lxml.html.fromstring(data)
	r = h.find_class('searchR')[0]
	lis = r.getchildren()
	data = []
	for li in lis:
		li_text = []
		for text in li.itertext():
			text = text.strip()
			if text:
				li_text.append(text)
		data.append(li_text)
		#print ' |$| '.join(li_text)
	return data



def fetch_one(**kwargs):
	p = dict(params)
	p.update(kwargs)
	return handle_fetch(http_get(url, p))

def start_fetch():
	fetch_one()

def fetch_all():
    savefile = open('/home/karvin/js/bj_schools.js','a+')
    for ds in bj_setting:#default_setting:
        d = dict({'provid':ds[0]})
        for area in ds[1]:
            d['area'] = area
            d['pg'] = 1
            data = fetch_one(**d)
            if not data:
                data = []
            schools = get_school(data)
            for school in schools:
                s =  '%s %s %s\r\n'%(province.get(ds[0]),district.get(area),school)
                savefile.write(s)
            page = 1
            while len(data) >0:
                page +=1
                d['pg'] = page
                data = fetch_one(**d)
                if not data:
                    data = []
                schools = get_school(data)
                for school in schools:
                    s =  '%s %s %s\r\n'%(province.get(ds[0]),district.get(area),school)
                    savefile.write(s)
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

default_setting = [('1',['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19']),
                   ('2',['20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','541']),
                   ('3',['38','39','40','41','42','43','44','45','46','47','48','49']),
                   ('4',['50','51','52','53','54','55','56','57','58','59','60','61']),
                   ('5',['75','76','77','78','79','80','81','82','83','84','85','86','87','88','89']),
                   ('6',['90','91','92','93','94','95','96','97','98','99']),
                   ('7',['114','116','117','118','119','120','121','122','123','124','125','126','127','128','129','130','132','132','133','134']),
                   ('8',['135','136','137','138','139','140','141','142','143','144','145','146','147','148','537']),
                   ('9',['149','150','151','152','153','154','155','156','157','158','159','538']),
                   ('10',['160','161','162','163','164','165','166','167','168','169','170','172','172','173','174','175','176','540']),
                   ('11',['177','178','179','180','181','182','183','184','185','186']),
                   ('12',['187','188','189','190','191','192','193','194','195','196','197','198']),
                   ('13',['199','200','201','202','203','204','205','206','207','208','209','210','211','212','213','214','215','216']),
                   ('14',['217','218','219','220','221','222','223','224','225','226','227','228','229','230','231','232','233','234','235']),
                   ('15',['62','63','64','65','66','67','68','69','70','71','72','73','74','555','556']),
                   ('16',['100','101','102','103','104','105','106','107','108','109','110','111','112','113']),
                   ('17',['236','237','238','239','240','241','242','243','244','245','246','247','248','249','250','251','252','253']),
                   ('18',['254','255','256','257','258','259','260','261','262','263','264','265','266','267','268']),
                   ('19',['269','270','271','272','273','274','275','276','277','278','279','280','281','282','283','284','285','286','287','288','289','290']),
                   ('20',['291','292','293','294','295','296','297','298','299','301','302','303','304','305','542','543','544']),
                   ('21',['306','307','308','309','310','311','312','313','314','315','316','317','318','319','320','321','322','323','324','325','326','539']),
                   ('22',['359','360','361','362','363','364','365','366','367','368','369','370','371','372','373','374','375','376','377','378','379','380']),
                   ('23',['327','328','329','330','331','332','333','334','335','336','337','338','339','340','341','342','343','344','345','346','347','348','349','350','351','352','353','354','355','356','357','358','545','546','547','548','549','550','551','552','553','554']),
                   ('24',['479','480','481','482','483','484','579','580','581','582','583','584','585','586','587','588','589','590','591','592','593','594','595','596','597','602']),
                   ('25',['381','382','383','384','385','386','387','388','389','390']),
                   ('26',['391','392','393','394','395','396','397','398','399','400','401','402','403','404','405','406','407']),
                   ('27',['408','409','410','411','412','413','414','415']),
                   ('28',['416','417','418','419','420','421','422','423','424','425','426']),
                   ('29',['427','428','429','430','431','432','433','434','435','436','437','438','439','440','441','557','558']),
                   ('30',['442','443','444','445','446','447','448','449','450']),
                   ('31',['451','452','453','454','455','599']),
                   ('32',['456','457','458','459','460','461','462','463','464','465','466','467','468','469','470','471','472','601','602']),
                   ('33',['474','476','559','560','561','562','563','564','565','566','567','568','569','570','571','572','573','574','575']),
                   ('34',['478','576','577','578'])]

if __name__ == '__main__':
	#start_fetch()
    fetch_all()
