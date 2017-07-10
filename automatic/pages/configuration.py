import json
import os
import shutil
import traceback

from ..utils.authentication import Authentication
from automatic.utils.config import Config
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from automatic.models import *
from .webpage import WEBPAGE


class CONFIG_PAGE(WEBPAGE):
    template = 'pages/configuration.html'
    request = None

    def __init__(self, request, type=None):
        self.request = request
        super().__init__(request, type)

    def render(self, request):
        title, tab_list = self.generate_nav_tabs(self.type)
        uid, username, login = self.render_user(request)
        return render_to_response(self.template,
                                  {'title': title, 'tabs': tab_list, 'login': login, 'uid': uid, 'username': username})

    @staticmethod
    def load_conf_content(cid, aid):
        if cid is None or aid is None:
            return []
        try:
            config = Config_File.objects.get(id=int(cid))
        except ObjectDoesNotExist as e:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '无法找到配置文件数据'}))
        file_name = config.filename
        prod = config.prod.name
        module = config.module.name
        if file_name is None or module is None:
            return []
        storage = CONFIG_PAGE.get_configuration_conf('storage')
        if storage[-1] != '/':
            storage += '/'
        if aid == 0:
            sid = 0
            hid = 0
            file = storage + prod + '/' + module + '/configurations/' + file_name
            if not os.path.isfile(file):
                content = ''
            else:
                f = open(file, 'r')
                content = f.read()
                f.close()
        else:
            p = Dep_Path.objects.get(id=aid)
            sid = p.host.server.id
            hid = p.host.id
            file = storage + prod + '/' + module + '/' + str(aid) + '/' + file_name
            if not os.path.isfile(file):
                content = ''
            else:
                f = open(file, 'r')
                content = f.read()
                f.close()
        return {'pid': config.prod.id, 'mid': config.module.id, 'cid': cid, 'sid': sid, 'hid': hid, 'aid': aid,
                'filename': config.filename, 'path': config.path, 'in_package': config.in_package,
                'active': config.active, 'content': content}

    @staticmethod
    def edit_config(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        j = json.loads(request.POST.get('request'))
        cid = j['cid']
        aid = j['aid']
        conf = j['conf']
        if int(cid) == 0 or int(aid) == 0 or cid == '' or aid == '':
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '配置文件或部署路径为空'}))
        storage = CONFIG_PAGE.get_configuration_conf('storage')
        if storage[-1] != '/':
            storage += '/'
        try:
            config = Config_File.objects.get(id=cid)
            conf_name = storage + config.prod.name + '/' + config.module.name + '/' + str(aid) + '/' + config.filename
            if os.path.isfile(conf_name):
                os.remove(conf_name)
            f = open(conf_name, 'w')
            f.write(conf)
            f.close()
        except Exception as e:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '配置文件修改失败。'}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '配置文件修改完成。'}))

    @staticmethod
    def get_configuration_conf(key):
        Config.load_config_type('configuration')
        config = Config()['configuration']
        return config[key]['value']

    @staticmethod
    def create_relation(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        j = json.loads(request.POST.get('request'))
        cid = j['cid']
        aid = j['aid']
        path = j['path']
        in_p = j['in_p']
        if int(cid) == 0 or int(aid) == 0:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '配置文件或部署路径为空'}))
        storage = CONFIG_PAGE.get_configuration_conf('storage')
        if storage[-1] != '/':
            storage += '/'
        try:
            c = Config_File.objects.get(id=cid)
            p = Dep_Path.objects.get(id=aid)
            cp_judge = Config_Path.objects.filter(pconf=c, dpath=p)
            if cp_judge.__len__() != 0:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '请勿重复关联'}))
            else:
                cp = Config_Path(pconf=c, dpath=p, active='Y', path=path, in_package=in_p)
                cp.save()
                src_conf = storage + c.prod.name + '/' + c.module.name + '/configurations/' + c.filename
                file_path = storage + c.prod.name + '/' + c.module.name + '/' + str(p.id)
                if not os.path.isdir(file_path):
                    os.makedirs(file_path)
                shutil.copy(src_conf, file_path)
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '关联失败：\n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '关联成功'}))

    @staticmethod
    def disrelation(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        cid = request.GET.get('cid')
        aid = request.GET.get('aid')
        if int(cid) == 0 or int(aid) == 0:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '配置文件或部署路径为空'}))
        storage = CONFIG_PAGE.get_configuration_conf('storage')
        if storage[-1] != '/':
            storage += '/'
        try:
            c = Config_File.objects.get(id=cid)
            p = Dep_Path.objects.get(id=aid)
            cp_judge = Config_Path.objects.filter(pconf=c, dpath=p)
            if cp_judge.__len__() == 0:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '尚未关联'}))
            else:
                cp_judge.delete()
                des_path = storage + c.prod.name + '/' + c.module.name + '/' + str(p.id) + '/'
                if os.path.isfile(des_path + c.filename):
                    os.remove(des_path + c.filename)
                if not os.listdir(des_path):
                    os.rmdir(des_path)
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '取消关联失败：\n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '取消关联成功'}))

    @staticmethod
    def load_data(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'cid' not in request.GET:
            cid = 0
        else:
            try:
                cid = int(request.GET.get('cid'))
            except Exception as e:
                print('获取配置文件ID出错: \n' + str(e) + '\n' + traceback.format_exc())
                cid = 0
        if 'aid' not in request.GET:
            aid = 0
        else:
            try:
                aid = int(request.GET.get('aid'))
            except Exception as e:
                print('获取项目ID出错: \n' + str(e) + '\n' + traceback.format_exc())
                aid = 0
        group_id = Authentication.verify_group(request)
        if group_id == 0:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '获取产品信息出错'}))
        elif group_id == 1:
            prods = Product.objects.all()
            servers = Dep_Server.objects.all()
        else:
            prods = Product.objects.filter(group_id=group_id)
            servers = Dep_Server.objects.filter(group_id=group_id)
        server_list = []
        host_list = {}
        path_list = {}
        prod_list = []
        module_list = {}
        config_list = {}
        for prod in prods:
            prod_list.append([prod.id, prod.name])
            config_list[prod.id] = {}
            module_list[str(prod.id)] = []
            modules = prod.modules.all()
            for module in modules:
                config_list[prod.id][module.id] = []
                module_list[str(prod.id)].append([module.id, module.name])
                configs = module.configs.all()
                for config in configs:
                    config_list[prod.id][module.id].append([config.id, config.filename])
        for server in servers:
            server_list.append([server.id, server.server])
            host_list[str(server.id)] = []
            path_list[server.id] = {}
            hosts = server.hosts.all()
            for host in hosts:
                path_list[server.id][host.id] = []
                host_list[str(server.id)].append([host.id, host.host])
                paths = host.paths.all()
                for path in paths:
                    path_list[server.id][host.id].append([path.id, path.module])
        if cid == 0:
            content = []
        else:
            content = CONFIG_PAGE.load_conf_content(cid, aid)
        return (True, json.JSONEncoder().encode({'status': 'OK',
                                                 'msg': {'server_list': server_list, 'host_list': host_list,
                                                         'path_list': path_list, 'prod_list': prod_list,
                                                         'module_list': module_list, 'config_list': config_list,
                                                         'content': content}}))

    @staticmethod
    def read_conf(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'mid' in request.GET:
            mid = request.GET.get('mid')
        if int(mid) == 0:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '产品或模块为空'}))
        storage = CONFIG_PAGE.get_configuration_conf('storage')
        if storage[-1] != '/':
            storage += '/'
        try:
            m = Prod_Module.objects.get(id=mid)
            config_path = storage + m.prod.name + '/' + m.name + '/configurations'
            if os.path.exists(config_path):
                dcfs = Config_File.objects.filter(prod=m.prod, module=m)
                configs = os.listdir(config_path)
                for dcf in dcfs:
                    if dcf.filename not in configs:
                        dcf.delete()
                    else:
                        configs.remove(dcf.filename)
                for confname in configs:
                    cf = Config_File(prod=m.prod, module=m, filename=confname, path='WEB-INF/classes/', in_package='Y',
                                     active='Y')
                    cf.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '读取失败：\n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '读取成功'}))

