import conf

from automatic.utils.config import Config
from automatic.models import *


class WEBPAGE():
    request = None
    conf = None
    type = None
    log = None

    def __init__(self, request, type=None):
        self.request = request
        if type is not None:
            self.type = type
            Config.load_config_type('ui_' + type)
            self.conf = Config()['ui_' + type]

    def generate_nav_tabs(self, activate=None):
        Config.load_config_type('ui_nav')
        navigation = Config()['ui_nav']
        nav_index = list(navigation.keys())
        nav_index.sort()
        tab_list = []
        title = ''
        if len(nav_index) > 0:
            title = navigation[nav_index[0]]['value']
        for index in nav_index:
            name = navigation[index]['value']
            code_name = navigation[index]['configuration']
            if activate == code_name:
                row = '<li class=\"active\"><a herf=\"#\">' + name + '</a></li>'
                title = navigation[index]['value']
            else:
                row = '<li><a href=\"?m=' + code_name + '\">' + name + '</a></li>'
            tab_list.append(row)
        return (title, tab_list)

    def get_conf(self, type):
        Config.load_config_type(type)
        return Config()[type]

    def get_public_key(self):
        rsa_keyfile = Config.get_config(type='env', name='rsa_keyfile')
        if rsa_keyfile is None:
            return None
        else:
            public_key_file = rsa_keyfile['value']


    def get_private_key(self):
        rsa_keyfile = Config.get_config(type='env', name='rsa_keyfile')
        if rsa_keyfile is None:
            return None
        else:
            return rsa_keyfile['configuration']

    def render_user(self, request):
        uid = conf.USER_ANONYMOUS
        username = conf.USER_ANONYMOUS_NAME
        response = "<a href=\"#\" onclick=\"show_login();\">登录 / 注册</a>"
        if 'login' in request.session.keys() and request.session['login']:
            if 'uid' in request.session.keys():
                uid = request.session['uid']
                if uid == conf.USER_ANONYMOUS:
                    request.session['login'] = False
                else:
                    try:
                        user = Auth.objects.get(id=request.session['uid'])
                        username = user.display
                    except:
                        request.session['login'] = False
                        request.session['uid'] = conf.USER_ANONYMOUS
            else:
                request.session['login'] = False
        if username != conf.USER_ANONYMOUS_NAME:
            response = username + "，欢迎！<a href=\"#\" onclick=\"logout();\">退出登录</a>"
        return (uid, username, response)

