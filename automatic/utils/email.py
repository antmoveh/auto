import os
import conf

from django.core.mail import EmailMultiAlternatives
from django.template import loader
from automatic.models import *

templates = {
    'build': 'build.html',
    'default': 'default.html',
    'deploy': 'deploy.html',
    'reset': 'reset.html',
    'test': 'test.html',
}


def mail(subject, mode='default', html_context={}, from_mail='bsp-auto@kokozu.net', to_mail=['zabbix@kokozu.net'],
         cc=None, text_content=''):
    admin = Auth.objects.get(id=conf.USER_ADMIN)
    if mode in templates:
        template = templates[mode]
    else:
        template = templates['default']
    t = loader.get_template(template)
    c = dict(html_context)
    html_content = t.render(c)
    if text_content is None or len(text_content) == 0:
        text_content = subject
    msg = EmailMultiAlternatives(subject, text_content, from_mail, to_mail, cc=cc, bcc=[admin.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def mail_attach(subject, body=None, from_mail='bsp-auto@kokozu.net', to_mail=['fushaosong@kokozu.net'], cc=None,
                file_location=None, result_list=None):
    msg = EmailMultiAlternatives(subject=subject, body=body, from_email=from_mail, to=to_mail, cc=cc)
    for result in result_list:
        file = file_location + result
        if os.path.isfile(file):
            of = open(file, 'rb')
            res = of.read().decode('utf-8')
            of.close()
            msg.attach(result, res, 'text/html')
    msg.send()

