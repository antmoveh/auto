import datetime
import json
import os
import traceback
import conf
from subprocess import Popen, PIPE
from django.db.utils import IntegrityError
from automatic.models import *


def login(request):
    if request is None:
        return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'})
    try:
        if 'u' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未提供登录用户'})
        if 'p' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未提供登录密码'})
        username = request.GET.get('u')
        if username == conf.USER_ANONYMOUS_NAME or username == conf.USER_DEFAULT_NAME:
            return False, json.JSONEncoder().encode({'status': 'FALSE', 'msg': '用户名/密码错误'})
        password = request.GET.get('p')
        users = Auth.objects.filter(username=username, active='Y')
        if len(users) == 1:
            user = users[0]
            status, password = hash_password(user.id, password)
            if not status:
                return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '用户登录出错: ' + str(password)})
            if password != user.password:
                return False, json.JSONEncoder().encode({'status': 'FALSE', 'msg': '用户名/密码错误'})
        elif len(users) == 0:
            return False, json.JSONEncoder().encode({'status': 'FALSE', 'msg': '未找到用户'})
        else:
            return False, json.JSONEncoder().encode({'status': 'FALSE', 'msg': '用户名重名'})
    except Exception as e:
        return False, json.JSONEncoder().encode(
            {'status': 'FAILED', 'msg': '登录失败: \n' + str(e) + '\n' + traceback.format_exc()})
    request.session['login'] = True
    request.session['uid'] = user.id
    return True, json.JSONEncoder().encode({'status': 'OK', 'msg': '登录成功'})


def hash_password(uid, password):
    system_name = os.name
    if system_name == 'nt':
        key_file = 'd:/' + str(uid) + '.key'
    elif system_name == 'posix':
        key_file = '/var/tmp/' + str(uid) + '.key'
    else:
        key_file = '/var/tmp/' + str(uid) + '.key'
    f = open(key_file, 'w')
    f.write(password)
    f.close()
    output, err = Popen(['md5sum', key_file], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
    os.remove(key_file)
    if len(err) > 0:
        return False, err.decode('utf-8')
    else:
        return True, output.decode('utf-8')[:32]


def new_user(request):
    if request is None:
        return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'})
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        display = request.POST.get('display')
        user = Auth(username=username, password=password, email=email, display=display, secret=datetime.datetime.now(),
                    active='Y')
        user.save()
        status, password = hash_password(user.id, user.password)
        if not status:
            user.delete()
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '添加新用户出错: ' + str(password)})
        user.password = password
        user.save()
    except IntegrityError as e:
        return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '用户已存在'})
    except Exception as e:
        return False, json.JSONEncoder().encode(
            {'status': 'FAILED', 'msg': '添加新用户出错: \n' + str(e) + '\n' + traceback.format_exc()})
    request.session['login'] = True
    request.session['uid'] = user.id
    return True, json.JSONEncoder().encode({'status': 'OK', 'msg': '注册成功'})


def logout(request):
    if request is None:
        return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'})
    request.session['login'] = False
    request.session['uid'] = conf.USER_ANONYMOUS
    return True, json.JSONEncoder().encode({'status': 'OK', 'msg': '退出成功'})
