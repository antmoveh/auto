import json
import traceback

from automatic.utils.authentication import Authentication
from automatic.utils.log import LOG
from django.shortcuts import render_to_response
from automatic.models import Dep_Server, Dep_Host, Dep_Path, Dep_Database
from .webpage import WEBPAGE


class SERVER_PAGE(WEBPAGE):
    template = 'pages/server.html'
    server_id = None

    def __init__(self, request, type=None):
        if 'sid' in request.GET:
            self.server_id = request.GET.get('sid')
        super().__init__(request, type)

    def render(self, request):
        title, tab_list = self.generate_nav_tabs(self.type)
        uid, username, login = self.render_user(request)
        return render_to_response(self.template,
                                  {'title': title, 'tabs': tab_list, 'login': login, 'uid': uid, 'username': username})

    @staticmethod
    def load_page(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        sid = None
        if 'sid' in request.GET:
            try:
                sid = int(request.GET.get('sid'))
            except:
                pass
        try:
            group_id = Authentication.verify_group(request)
            if group_id == 0:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '获取项目信息出错'}))
            elif group_id == 1:
                server_list = Dep_Server.objects.all()
            else:
                server_list = Dep_Server.objects.filter(group_id=group_id)
            servers = []
            server_info = {}
            for s in server_list:
                servers.append([s.id, s.server])
                if s.id == sid:
                    host_list = s.hosts.all()
                    hosts = []
                    for h in host_list:
                        path_list = h.paths.all()
                        paths = []
                        for p in path_list:
                            paths.append(
                                {'id': p.id, 'module': p.module, 'src_name': p.src_name, 'des_path': p.des_path,
                                 'des_name': p.des_name})
                        hosts.append(
                            {'id': h.id, 'host_address': h.host, 'ssh_port': h.ssh_port, 'ssh_user': h.ssh_user,
                             'ssh_pass': h.ssh_pass, 'ssh_key': h.ssh_file, 'paths': paths})
                    dbs = s.databases.all()
                    databases = []
                    for db in dbs:
                        databases.append(
                            {'id': db.id, 'db_module': db.database, 'db_host': db.db_host, 'db_port': db.db_port,
                             'db_name': db.db_name, 'db_user': db.db_user, 'db_pass': db.db_pass})
                    server_info = {'id': s.id, 'name': s.server, 'production': s.production, 'active': s.active,
                                   'hosts': hosts, 'databases': databases}
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取项目信息出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (
                True,
                json.JSONEncoder().encode({'status': 'OK', 'msg': {'servers': servers, 'server_info': server_info}}))

    def get_server_list(self):
        server_list = Dep_Server.objects.all()
        servers = []
        for server in server_list:
            if server.id == self.server_id:
                server_id = -1
            else:
                server_id = server.id
            server_info = "[" + str(server_id) + ", \"" + server.server + "\"],"
            servers.append(server_info)
        return servers

    def get_server_info(self):
        try:
            server = Dep_Server.objects.get(id=self.server_id)
        except Exception as e:
            LOG('default').error('[服务器管理]获取服务器信息错误：\n' + str(e) + '\n' + traceback.format_exc())
            return []
        hosts = server.hosts.all()
        databases = server.databases.all()
        server_info = []
        server_info.append('\"id\": \"' + str(server.id) + '\",')
        server_info.append('\"name\": \"' + str(server.server) + '\",')
        server_info.append('\"active\": \"' + str(server.active) + '\",')
        server_info.append('\"hosts\": [')
        for h in hosts:
            server_info.append('{')
            server_info.append('\"id\": \"' + str(h.id) + '\",')
            server_info.append('\"host_address\": \"' + h.host + '\",')
            server_info.append('\"ssh_port\": \"' + h.ssh_port + '\",')
            server_info.append('\"ssh_user\": \"' + h.ssh_user + '\",')
            server_info.append('\"ssh_pass\": \"' + h.ssh_pass + '\",')
            server_info.append('\"ssh_key\": \"' + h.ssh_file + '\",')
            server_info.append('\"paths\": [')
            paths = h.paths.all()
            for p in paths:
                server_info.append('{')
                server_info.append('\"id\": \"' + str(p.id) + '\",')
                server_info.append('\"module\": \"' + p.module + '\",')
                server_info.append('\"src_name\": \"' + p.src_name + '\",')
                server_info.append('\"des_path\": \"' + p.des_path + '\",')
                server_info.append('\"des_name\": \"' + p.des_name + '\",')
                server_info.append('},')
            server_info.append('],')
            server_info.append('},')
        server_info.append('],')
        server_info.append('\"databases\": [')
        for db in databases:
            server_info.append('{')
            server_info.append('\"id\": \"' + str(db.id) + '\",')
            server_info.append('\"db_module\": \"' + db.database + '\",')
            server_info.append('\"db_host\": \"' + db.db_host + '\",')
            server_info.append('\"db_port\": \"' + db.db_port + '\",')
            server_info.append('\"db_name\": \"' + db.db_name + '\",')
            server_info.append('\"db_user\": \"' + db.db_user + '\",')
            server_info.append('\"db_pass\": \"' + db.db_pass + '\",')
            server_info.append('},')
        server_info.append('],')
        return server_info

    @staticmethod
    def edit_server(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        try:
            r = request.POST.get('request')
            j = json.loads(r)
            server_id = int(j['server_id'])
            server_name = j['server_name']
            production = j['production']
            hosts = j['hosts']
            databases = j['databases']
            if server_id == 0:
                group_id = Authentication.verify_group(request)
                if group_id == 0:
                    return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '创建项目出错'}))
                server = Dep_Server(server=server_name, production=production, active='Y', group_id=group_id)
            else:
                server = Dep_Server.objects.get(id=server_id)
                server.server = server_name
            server.save()
            old_hosts = server.hosts.all()
            o_hs = []
            for o_h in old_hosts:
                o_hs.append(o_h.id)
            for host in hosts:
                host_id = int(host['id'])
                if host_id == 0:
                    h = Dep_Host(server=server, host=host['host_address'], ssh_port=host['ssh_port'],
                                 ssh_user=host['ssh_user'], ssh_pass=host['ssh_pass'], ssh_file=host['ssh_key'])
                else:
                    o_hs.remove(host_id)
                    h = Dep_Host.objects.get(id=host_id)
                    h.host = host['host_address']
                    h.ssh_port = host['ssh_port']
                    h.ssh_user = host['ssh_user']
                    h.ssh_pass = host['ssh_pass']
                    h.ssh_file = host['ssh_key']
                h.save()
                paths = host['paths']
                old_paths = h.paths.all()
                o_ps = []
                for o_p in old_paths:
                    o_ps.append(o_p.id)
                for path in paths:
                    path_id = int(path['id'])
                    if path_id == 0:
                        p = Dep_Path(host=h, module=path['path_module'], work_mod='WAR', src_name=path['path_src'],
                                     des_path=path['path'], des_name=path['path_des'])
                    else:
                        o_ps.remove(path_id)
                        p = Dep_Path.objects.get(id=path_id)
                        p.module = path['path_module']
                        p.src_name = path['path_src']
                        p.des_path = path['path']
                        p.des_name = path['path_des']
                    p.save()
                for del_pid in o_ps:
                    del_p = Dep_Path.objects.get(id=del_pid)
                    del_p.delete()
            for del_hid in o_hs:
                del_h = Dep_Host.objects.get(id=del_hid)
                paths = del_h.paths.all()
                paths.delete()
                del_h.delete()
            old_dbs = server.databases.all()
            o_dbs = []
            for o_db in old_dbs:
                o_dbs.append(o_db.id)
            for db in databases:
                db_id = int(db['id'])
                if db_id == 0:
                    d = Dep_Database(server=server, database=db['db_module'], db_type='MYSQL', db_name=db['db_name'],
                                     db_host=db['db_host'], db_port=db['db_port'], db_user=db['db_user'],
                                     db_pass=db['db_pass'])
                else:
                    o_dbs.remove(db_id)
                    d = Dep_Database.objects.get(id=db_id)
                    d.database = db['db_module']
                    d.db_name = db['db_name']
                    d.db_host = db['db_host']
                    d.db_port = db['db_port']
                    d.db_user = db['db_user']
                    d.db_pass = db['db_pass']
                d.save()
            for del_dbid in o_dbs:
                del_db = Dep_Database.objects.get(id=del_dbid)
                del_db.delete()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '项目改动失败：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            if server_id == 0:
                return (True, json.JSONEncoder().encode({'status': 'NEW', 'msg': server.id}))
            else:
                return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '项目改动成功'}))

    @staticmethod
    def disable_server(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        if 'sid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定项目'}))
        try:
            sid = int(request.GET.get('sid'))
            s = Dep_Server.objects.get(id=sid)
            if s.active == 'Y':
                s.active = 'N'
            else:
                s.active = 'Y'
            s.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '修改项目状态出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': s.active}))

    @staticmethod
    def set_server_production(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        if 'sid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定项目'}))
        try:
            sid = int(request.GET.get('sid'))
            s = Dep_Server.objects.get(id=sid)
            if s.production == 'Y':
                s.production = 'N'
            else:
                s.production = 'Y'
            s.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '修改项目状态出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': s.production}))

    @staticmethod
    def delete_server(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        if 'sid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定项目'}))
        try:
            sid = int(request.GET.get('sid'))
            s = Dep_Server.objects.get(id=sid)
            hs = s.hosts.all()
            for h in hs:
                p = h.paths.all()
                p.delete()
            hs.delete()
            db = s.databases.all()
            db.delete()
            d = s.dbs.all()
            d.delete()
            s.delete()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '删除项目出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': ''}))
