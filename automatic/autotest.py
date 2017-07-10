import json
import conf
from .utils.authentication import Authentication
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .pages.execdb import EXECDB_PAGE
from .pages.test import TEST_PAGE
from .pages.user_group import USER_GROUP_PAGE


@csrf_exempt
def action(request):
    response = 'action'
    if 'a' in request.GET:
        action = request.GET.get('a')
        if action == 'gcl':
            status, r = TEST_PAGE.get_caselist(request)
            response = r
        if action == 'edc':
            status, r = TEST_PAGE.edit_case(request)
            response = r
        if action == 'gtc':
            status, r = TEST_PAGE.get_test_conf(request)
            response = r
        if action == 'dc':
            status, r = TEST_PAGE.delete_conf(request)
            response = r
        if action == 'sat':
            status, r = TEST_PAGE.submit_action(request)
            response = r
        if action == 'sap':
            status, r = TEST_PAGE.show_para(request)
            response = r
        if action == 'sae':
            status, r = TEST_PAGE.submit_area(request)
            response = r
        if action == 'noy':
            status, r = TEST_PAGE.check_testcase(request)
            response = r
        if action == 'msae':
            status, r = TEST_PAGE.manage_submit_area(request)
            response = r
    return HttpResponse(response)


@csrf_exempt
def action_login(request):
    response = 'action_login'
    if 'login' in request.session and request.session['login']:
        if 'uid' in request.session:
            uid = request.session['uid']
        if 'a' in request.GET:
            action = request.GET.get('a')
            if action == 'eca':
                status, r = TEST_PAGE.execute_action(request)
                response = r
            if action == 'saj':
                status, r = TEST_PAGE.submit_show_param(request)
                response = r
            if action == 'smp':
                status, r = TEST_PAGE.show_param(request)
                response = r
            if action == 'dsap':
                status, r = TEST_PAGE.show_action_param(request)
                response = r
            if action == 'dscp':
                status, r = TEST_PAGE.show_case_param(request)
                response = r
            if action == 'dsmp':
                status, r = TEST_PAGE.deploy_show_param(request)
                response = r
            if action == 'dsa':
                status, r = TEST_PAGE.deploy_submit_area(request)
                response = r
            if action == 'drc':
                status, r = TEST_PAGE.deploy_run_case(request)
                response = r
            if action == 'srl':
                status, r = TEST_PAGE.show_result_list(request)
                response = r
            if action == 'sr':
                status, r = TEST_PAGE.show_result(request)
                response = r
    else:
        response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
    return HttpResponse(response)


# 提示信息
@csrf_exempt
def hint_login(request):
    response = 'action_login'
    uid = conf.USER_ANONYMOUS
    if 'login' in request.session and request.session['login']:
        if 'a' in request.GET:
            action = request.GET.get('a')
            if action == 'gdb':
                status, r = EXECDB_PAGE.get_dbs(request)
                response = r
    else:
        response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
    return HttpResponse(response)


@csrf_exempt
def auto_script_main(request):
    response = 'auto_script'
    if 'a' in request.GET:
        action = request.GET.get('a')
        uid = conf.USER_ANONYMOUS
        if 'login' in request.session and request.session['login']:
            if 'uid' in request.session:
                uid = request.session['uid']
            else:
                request.session['login'] = False
                request.session['uid'] = conf.USER_ANONYMOUS
                request.session['user'] = conf.USER_ANONYMOUS_NAME
        try:
            auth = Authentication(uid)
        except:
            uid = conf.USER_ANONYMOUS
            auth = Authentication(conf.USER_ANONYMOUS)
        if action == 'adc':
            type = 'TEST_PAGE'
            if auth.verify_action(type, action):
                status, r = TEST_PAGE.edit_case(request)
                response = r
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        if action == 'dec':
            type = 'TEST_PAGE'
            if auth.verify_action(type, action):
                status, r = TEST_PAGE.delete_case(request)
                response = r
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
    else:
        response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
    return HttpResponse(response)


@csrf_exempt
def upload(request):
    cid = TEST_PAGE.upload_file(request)
    return HttpResponseRedirect('/?m=test&cid=' + cid)


@csrf_exempt
def user_group(request):
    response = 'user_group'
    if 'a' in request.GET:
        action = request.GET.get('a')
        uid = conf.USER_ANONYMOUS
        if 'login' in request.session and request.session['login']:
            if 'uid' in request.session:
                uid = request.session['uid']
            else:
                request.session['login'] = False
                request.session['uid'] = conf.USER_ANONYMOUS
                request.session['user'] = conf.USER_ANONYMOUS_NAME
        try:
            auth = Authentication(uid)
        except:
            uid = conf.USER_ANONYMOUS
            auth = Authentication(conf.USER_ANONYMOUS)
        if action == 'ugp':
            type = 'USER_GROUP'
            if auth.verify_action(type, action):
                status, r = USER_GROUP_PAGE.load_data(request)
                response = r
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        elif action == 'agu':
            type = 'USER_GROUP'
            if auth.verify_action(type, action):
                status, r = USER_GROUP_PAGE.add_group(request)
                response = r
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        elif action == 'dgu':
            type = 'USER_GROUP'
            if auth.verify_action(type, action):
                status, r = USER_GROUP_PAGE.delete_group(request)
                response = r
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        elif action == 'mug':
            type = 'USER_GROUP'
            if auth.verify_action(type, action):
                status, r = USER_GROUP_PAGE.move_user(request)
                response = r
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})

    else:
        response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
    return HttpResponse(response)
