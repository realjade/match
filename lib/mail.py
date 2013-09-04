# -*- coding: utf-8 -*-
import base64
import os,sys
import smtplib
from email.mime.text import MIMEText
from jinja2 import FileSystemLoader, Environment, StrictUndefined
from flask import current_app

app_path = os.path.dirname(os.path.abspath(__name__))
env = Environment(loader=FileSystemLoader(os.path.join(app_path, 'templates/email')),
                  undefined = StrictUndefined,auto_reload = True)

templatedict = {'forget':('password.html',u'背书吧密码重置邮件'),
                'classtask':('classtask.html',u'背书吧作业'),
                'invitataion':('invitation.html',u'背书吧邀请信'),
                }

def load_email_content(name, **kwargs):
    if name[-4:] == '.htm':
        name = name[:-4] + '.html'
    if name[-5:] != '.html':
        name += '.html'
    template = env.get_template(name)
    return template.render(**kwargs)

def email_base64(s):
    return '=?utf-8?b?%s?='%(base64.b64encode(s.encode('utf-8')))

def smtp_send_mail(to, message, mailtype='html', debug=False):
    me = current_app.config['SMTP_SENDER']
    eventtype = message['event']
    source = templatedict.get(eventtype)[0]
    subject = templatedict.get(eventtype)[1]
    content = load_email_content(source,**message)
    fromemail = current_app.config['FROM_EMAIL']
    msg = MIMEText(content, mailtype, 'utf-8')
    msg['Subject'] = subject 
    msg['From'] = email_base64(current_app.config['SENDER_NICKNAME']) + ' <%s>'%(fromemail)
    msg['To'] = ' '.join(to)
    msg['Reply-To'] = fromemail
    msg.set_charset('utf-8')
    
    try:
        s = smtplib.SMTP(current_app.config['SMTP_SERVER'])
        if debug:
            s.set_debuglevel(1)
        s.login(me, current_app.config['SMTP_SENDER_PASSWORD'])
        s.sendmail(fromemail, to, msg.as_string())
        s.quit()
        return True
    except:
        return False
    
