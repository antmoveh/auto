import datetime
import json
import traceback
import conf
import automatic.utils.email as EMAIL
import automatic.utils.login as LOGIN

from automatic.utils.authentication import Authentication
from automatic.utils.config import Config
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from automatic.models import *
from .webpage import WEBPAGE


class USER_PAGE(WEBPAGE):
    template = 'pages/user.html'

    def __init__(self, request, type=None):
        super().__init__(request, type)

    def render(self, request):
        title, tab_list = self.generate_nav_tabs(self.type)
        uid, username, login = self.render_user(request)
        return render_to_response(self.template,
                                  {'title': title, 'tabs': tab_list, 'login': login, 'uid': uid, 'username': username})

    @staticmethod
    def show_reset_pass(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'u' not in request.GET and 's' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'Input not found'}))
        username = request.GET.get('u')
        secret = request.GET.get('s')
        try:
            user = Auth.objects.get(username=username)
        except ObjectDoesNotExist:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'Cannot find user.'}))
        print(user.password + str(user.secret))
        status, check_string = LOGIN.hash_password(user.id, user.password + str(user.secret))
        if secret != check_string:
            return (
            False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'Invalid reset request. ' + check_string}))
        max_diff = datetime.timedelta(hours=8)
        if datetime.datetime.now() - user.secret > max_diff:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'Reset request expired.'}))
        user.password = '550e1bafe077ff0b0b67f4e32f29d751'
        user.save()
        request.session['login'] = True
        request.session['uid'] = user.id
        return (True, render_to_response('pages/reset.html', {'uname': user.display}))


    @staticmethod
    def load_data(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        uid = conf.USER_ANONYMOUS
        if 'login' in request.session.keys() and request.session['login']:
            uid = request.session['uid']
        try:
            auth = Auth.objects.get(id=uid)
        except Exception as e:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '无法找到用户'}))
        user_info = {'username': auth.username, 'display': auth.display, 'email': auth.email}
        user_permissions = []
        permissions = []
        prod_list = []
        server_list = []
        subscribe_list = {}
        if uid == conf.USER_ADMIN:
            pers = User_Permission.objects.filter(active='Y').order_by("type")
            per_type = ""
            per_actions = []
            for permission in pers:
                if per_type != permission.type:
                    if len(per_type) > 0:
                        permissions.append({'type': per_type, 'actions': per_actions})
                    per_type = permission.type
                    per_actions = []
                per_actions.append({'id': permission.id, 'name': permission.name})
            if len(per_type) > 0:
                permissions.append({'type': per_type, 'actions': per_actions})
            users = Auth.objects.all()
            for user in users:
                user_permission = {'uid': user.id, 'username': user.username, 'display': user.display,
                                   'active': user.active, 'permissions': []}
                u_p_rs = User_UserPermission.objects.filter(user=user)
                for u_p_r in u_p_rs:
                    user_permission['permissions'].append(u_p_r.permission.id)
                user_permissions.append(user_permission)
        else:
            available_prods = [0]
            available_servers = [0]
            #	prod_list.append({'id': 0, 'name': '全部'})
            #	server_list.append({'id': 0, 'name': '全部'})
            group_id = Authentication.verify_group(request)
            if group_id == 0:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '获取产品信息出错'}))
            elif group_id == 1:
                prods = Product.objects.filter(active='Y').order_by('name')
                servers = Dep_Server.objects.filter(active='Y').order_by('server')
            else:
                prods = Product.objects.filter(active='Y', group_id=group_id).order_by('name')
                servers = Dep_Server.objects.filter(active='Y', group_id=group_id).order_by('server')
            subscribes = User_Subscribe.objects.filter(user=auth).order_by('prod_id')
            current_prod = -1
            subscribe_servers = {}
            for prod in prods:
                prod_list.append({'id': prod.id, 'name': prod.name})
                available_prods.append(prod.id)
            for server in servers:
                server_list.append({'id': server.id, 'name': server.server})
                available_servers.append(server.id)
            for subscribe in subscribes:
                if subscribe.prod_id in available_prods and (
                        subscribe.server_id in available_servers or subscribe.server_id == -1):
                    if subscribe.prod_id != current_prod:
                        if current_prod > -1:
                            subscribe_list[current_prod] = subscribe_servers
                        subscribe_servers = {}
                        current_prod = subscribe.prod_id
                    subscribe_servers[subscribe.server_id] = {'id': subscribe.id, 'prod': subscribe.prod_id,
                                                              'server': subscribe.server_id, 'deploy': subscribe.deploy,
                                                              'test': subscribe.test}
            if len(subscribe_servers) > 0:
                subscribe_list[current_prod] = subscribe_servers
        response = {'user_info': user_info, 'user_permissions': user_permissions, 'permissions': permissions,
                    'prod_list': prod_list, 'server_list': server_list, 'subscribe_list': subscribe_list}
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': response}))

    @staticmethod
    def disable_user(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'u' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定用户'}))
        try:
            uid = int(request.GET.get('u'))
            if uid == conf.USER_ADMIN or uid == conf.USER_ANONYMOUS or uid == conf.USER_DEFAULT:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '不可禁用内置用户'}))
            user = Auth.objects.get(id=uid)
            if user.active == 'Y':
                user.active = 'N'
            else:
                user.active = 'Y'
            user.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '启用/禁用用户发生异常: ' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': user.active}))

    @staticmethod
    def rm_user(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'u' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定用户'}))
        try:
            uid = int(request.GET.get('u'))
            if uid == conf.USER_ADMIN or uid == conf.USER_ANONYMOUS or uid == conf.USER_DEFAULT:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '不可删除内置用户'}))
            user = Auth.objects.get(id=uid)
            if user.active != 'N':
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '只能删除禁用用户'}))
            d_user = User_Deleted_User(user_id=user.id, username=user.username, email=user.email, display=user.display)
            d_user.save()
            permits = User_UserPermission.objects.filter(user=user)
            for permit in permits:
                permit.delete()
            user.delete()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '删除用户发生异常: ' + str(str(e) + '\n' + traceback.format_exc())}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': 'OK'}))

    @staticmethod
    def update_user_permit(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'u' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定用户'}))
        try:
            uid = int(request.GET.get('u'))
            user = Auth.objects.get(id=uid)
            permits = json.loads(request.POST.get('permits'))
            #print('permits: ' + str(permits))
            user_permits = User_UserPermission.objects.filter(user=user)
            for permit in user_permits:
                #print(str(permit.permission.id) + ' count: ' + str(permits.count(permit.permission.id)))
                if permits.count(str(permit.permission.id)) > 0:
                    permits.remove(str(permit.permission.id))
                else:
                    permit.delete()
            for per in permits:
                p = User_Permission.objects.get(id=per)
                user_per = User_UserPermission(user=user, permission=p)
                user_per.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '用户权限修改发生异常: ' + str(str(e) + '\n' + traceback.format_exc())}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '用户权限修改成功'}))

    @staticmethod
    def update_userinfo(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        try:
            if 'login' in request.session.keys() and request.session['login']:
                uid = request.session['uid']
            else:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未登录'}))
            user = Auth.objects.get(id=uid)
            display = request.POST.get('display')
            email = request.POST.get('email')
            user.display = display
            user.email = email
            if 'password' in request.POST and 'old_password' in request.POST:
                password = request.POST.get('password')
                old_password = request.POST.get('old_password')
                if password is not None and len(password) > 0 and old_password is not None and len(old_password) > 0:
                    status, old_password = LOGIN.hash_password(user.id, old_password)
                    if not status:
                        return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': old_password}))
                    if password is not None and len(password) > 7:
                        if old_password != user.password:
                            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '密码错误'}))
                        status, password = LOGIN.hash_password(user.id, password)
                        if not status:
                            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': password}))
                        user.password = password
            user.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '修改用户信息发生异常: ' + str(str(e) + '\n' + traceback.format_exc())}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '修改用户信息成功'}))

    @staticmethod
    def update_subscribe(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'check_list' not in request.POST or 'build_list' not in request.POST or 'check_list_o' not in request.POST or 'build_list_o' not in request.POST:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未提供列表'}))
        try:
            if 'login' in request.session.keys() and request.session['login']:
                uid = request.session['uid']
            else:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未登录'}))
            user = Auth.objects.get(id=uid)
            check_list = json.loads(request.POST.get('check_list'))
            build_list = json.loads(request.POST.get('build_list'))
            build_list_o = json.loads(request.POST.get('build_list_o'))
            check_list_o = json.loads(request.POST.get('check_list_o'))
            build_s = User_Subscribe.objects.filter(user=user, server_id=-1)
            server_s = User_Subscribe.objects.filter(user=user).exclude(server_id=-1)
            deleted_b = []
            new_b = []
            deleted_s = []
            new_s = []
            for b_s in build_s:
                if str(b_s.id) not in build_list_o.keys():
                    deleted_b.append(str(b_s.prod_id))
                    b_s.delete()
            for b in build_list:
                u_s = User_Subscribe(user=user, prod_id=int(b), server_id=-1, deploy='N', test='N')
                u_s.save()
                new_b.append({'bid': str(u_s.id), 'pid': str(u_s.prod_id)})
            for s_s in server_s:
                s_key = str(s_s.id)
                if s_key not in check_list_o.keys():
                    deleted_s.append({'pid': str(s_s.prod_id), 'sid': str(s_s.server_id)})
                    s_s.delete()
                else:
                    s_s.deploy = check_list_o[s_key]["deploy"]
                    s_s.test = check_list_o[s_key]["test"]
                    s_s.save()
            for s in check_list:
                u_s_s = User_Subscribe(user=user, prod_id=int(s["pid"]), server_id=int(s["sid"]), deploy=s["deploy"],
                                       test=s["test"])
                u_s_s.save()
                new_s.append({'fid': str(u_s_s.id), 'pid': str(u_s_s.prod_id), 'sid': str(u_s_s.server_id)})
            r = {'info': '更新邮件订阅成功', 'd_b': deleted_b, 'n_b': new_b, 'd_s': deleted_s, 'n_s': new_s}
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '更新邮件订阅发生异常: ' + str(str(e) + '\n' + traceback.format_exc())}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': r}))

    @staticmethod
    def apply_reset_pass(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'u' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '信息不全'}))
        username = request.GET.get('u')
        try:
            user = Auth.objects.get(username=username)
        except ObjectDoesNotExist:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '无法找到指定用户'}))
        try:
            now = datetime.datetime.now()
            user.secret = now
            user.save()
            print((user.password + str(user.secret))[:-7])
            status, reset_string = LOGIN.hash_password(user.id, user.password + str(user.secret)[:-7])
            bsp_url = Config.get_config('env', 'bsp_url')['value']
            url = 'http://' + bsp_url + '/user/?a=snp&u=' + user.username + '&s=' + reset_string
            print(url)
            subject = '自动化平台密码重置'
            context = {'url': url}
            cc = []
            EMAIL.mail(subject=subject, mode='reset', html_context=context, to_mail=[user.email], cc=cc,
                       text_content='使用该地址找回密码: ' + url)
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '申请重置密码发生异常: ' + str(str(e) + '\n' + traceback.format_exc())}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '重置密码申请成功，请查收邮件'}))

    @staticmethod
    def reset_pass(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'op' not in request.GET or 'p' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '信息不全'}))
        try:
            user = Auth.objects.get(id=request.session['uid'])
        except ObjectDoesNotExist:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '无法找到指定用户'}))
        try:
            old_password = request.GET.get('op')
            password = request.GET.get('p')
            status, old_password = LOGIN.hash_password(user.id, old_password)
            if old_password != user.password:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '原密码错误'}))
            status, password = LOGIN.hash_password(user.id, password)
            user.password = password
            user.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '重置密码发生异常: ' + str(str(e) + '\n' + traceback.format_exc())}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '重置密码成功'}))
