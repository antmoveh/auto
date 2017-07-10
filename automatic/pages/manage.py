import json
import traceback

from automatic.utils.SSH import SSHHelper
from automatic.utils.authentication import Authentication
from django.shortcuts import render_to_response
from automatic.models import *
from .webpage import WEBPAGE


class MANAGE_PAGE(WEBPAGE):
    template = 'pages/manage.html'

    def __init__(self, request, type=None):
        super().__init__(request, type)

    def render(self, request):
        title, tab_list = self.generate_nav_tabs(self.type)
        uid, username, login = self.render_user(request)
        return render_to_response(self.template,
                                  {'title': title, 'tabs': tab_list, 'login': login, 'uid': uid, 'username': username})

    @staticmethod
    def load_data(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        prod_list = []
        module_list = {}
        group_id = Authentication.verify_group(request)
        if group_id == 0:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '获取产品信息出错'}))
        elif group_id == 1:
            prods = Product.objects.all()
            servers = Dep_Server.objects.filter(active='Y')
        else:
            prods = Product.objects.filter(group_id=group_id)
            servers = Dep_Server.objects.filter(active='Y', group_id=group_id)
        for prod in prods:
            prod_list.append([prod.id, prod.name, prod.active])
            module_list[str(prod.id)] = []
            modules = prod.modules.all()
            for module in modules:
                module_list[str(prod.id)].append([module.id, module.name, module.active])
        test_tasks = AutoTest_action.objects.all()
        task_list = []
        for t in test_tasks:
            task_list.append([t.id, t.name])
        jenkins = Prod_Jenkins.objects.filter(active='Y')
        jenkins_list = []
        for j in jenkins:
            jenkins_list.append([j.id, j.name])
        server_list = []
        host_list = {}
        for server in servers:
            server_list.append([server.id, server.server, server.active])
            hosts = server.hosts.all()
            s_hosts = []
            for host in hosts:
                paths = []
                path_list = host.paths.all()
                for path in path_list:
                    paths.append(path.module)
                s_hosts.append([host.id, host.host, paths])
            host_list[server.id] = s_hosts
        actions = []
        test_list = []
        if 'pid' in request.GET and 's' in request.GET:
            try:
                pid = int(request.GET.get('pid'))
                sid = int(request.GET.get('s'))
                if 'h' in request.GET:
                    hid = int(request.GET.get('h'))
                else:
                    hid = 0
            except Exception as e:
                return (
                False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': str(e) + '\n' + traceback.format_exc()}))
            action_list = Dep_Action.objects.filter(server_id=sid, host_id=hid, prod_id=pid).order_by('sequence')
            if len(action_list) > 0:
                for a in action_list:
                    detail = {'aid': str(a.id), 'operation': a.operation, 'param1': a.param1, 'param2': a.param2,
                              'param3': a.param3, 'param4': a.param4, 'param5': a.param5, 'active': a.active}
                    actions.append(detail)
            p = Product.objects.get(id=pid)
            s = Dep_Server.objects.get(id=sid)
            # tests = Prod_TestJob.objects.filter(prod = p, server = s)
            #	for t in tests:
            #		test_list.append({'id': t.id, 'name': t.name, 'active': t.active})
            test_list = ''
            test_j = AutoTest_Job.objects.filter(prod=p, server=s)
            if test_j.count() > 0:
                for t in test_j:
                    test_list = t.test_job
        data = {'prod_list': prod_list, 'module_list': module_list, 'task_list': task_list, 'server_list': server_list,
                'host_list': host_list, 'actions': actions, 'test_list': test_list, 'jenkins': jenkins_list}
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': data}))

    @staticmethod
    def add_prod(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        try:
            if 'pid' not in request.GET:
                pid = 0
            else:
                pid = int(request.GET.get('pid'))
            post_data = request.POST.get('prod_name')
            prod_name = post_data
            if pid == 0:
                group_id = Authentication.verify_group(request)
                if group_id == 0:
                    return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '创建产品出错'}))
                prod = Product(name=prod_name, active='Y', group_id=group_id)
            else:
                prod = Product.objects.get(id=pid)
                prod.name = prod_name
            prod.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '添加/更新产品发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '添加/更新产品成功'}))

    @staticmethod
    def disable_prod(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'pid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定产品'}))
        try:
            pid = int(request.GET.get('pid'))
            prod = Product.objects.get(id=pid)
            if prod.active == 'Y':
                prod.active = 'N'
            else:
                prod.active = 'Y'
            prod.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '启用/禁用产品发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': prod.active}))

    @staticmethod
    def add_module(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'pid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定产品'}))
        try:
            pid = int(request.GET.get('pid'))
            prod = Product.objects.get(id=pid)
            post_data = request.POST.get('module')
            module_name = post_data
            test_module = Prod_Module.objects.filter(prod=prod, name=module_name)
            if len(test_module) > 0:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '添加子模块发生异常: 同名子模块已经存在'}))
            module = Prod_Module(prod=prod, name=module_name, active='Y')
            module.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '添加子模块发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '添加子模块成功'}))

    @staticmethod
    def edit_module(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'mid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定子模块'}))
        try:
            mid = int(request.GET.get('mid'))
            post_data = request.POST.get('module_name')
            module_name = post_data
            if len(module_name) < 1:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '子模块名称不可为空'}))
            module = Prod_Module.objects.get(id=mid)
            if module.name == module_name:
                return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '更新子模块成功'}))
            test_module = Prod_Module.objects.filter(prod=module.prod, name=module_name)
            if len(test_module) > 0:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '更新子模块发生异常: 同名子模块已经存在'}))
            module.name = module_name
            module.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '更新子模块发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '更新子模块成功'}))

    @staticmethod
    def disable_module(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'mid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定子模块'}))
        try:
            mid = int(request.GET.get('mid'))
            module = Prod_Module.objects.get(id=mid)
            if module.active == 'Y':
                module.active = 'N'
            else:
                module.active = 'Y'
            module.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '启用/禁用子模块发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': module.active}))

    @staticmethod
    def rm_module(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'mid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定子模块'}))
        try:
            mid = int(request.GET.get('mid'))
            module = Prod_Module.objects.get(id=mid)
            module.delete()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '删除子模块发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '删除子模块成功'}))

    @staticmethod
    def rm_product(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'pid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定产品'}))
        try:
            pid = int(request.GET.get('pid'))
            product = Product.objects.get(id=pid)
            product.delete()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '删除产品发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '删除产品发生异常'}))

    @staticmethod
    def edit_buildjob(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'mid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定子模块'}))
        try:
            mid = int(request.GET.get('mid'))
            buildjob = json.loads(request.POST.get('buildjob'))
            module = Prod_Module.objects.get(id=mid)
            mod = buildjob['mod']
            j_id = int(buildjob['jenkins'])
            jenkins = Prod_Jenkins.objects.get(id=j_id)
            job_name = buildjob['job_name']
            token = buildjob['token']
            git_url = buildjob['git_url']
            code_path = buildjob['code_path']
            sql_path = buildjob['sql_path']
            b = Prod_BuildJobs.objects.filter(module=module)
            if len(b) < 1:
                b = Prod_BuildJobs(prod=module.prod, module=module, jenkins=jenkins, job_name=job_name, token=token,
                                   git_url=git_url, code_path=code_path, sql_path=sql_path, mod=mod)
            else:
                b = b[0]
                b.jenkins = jenkins
                b.job_name = job_name
                b.token = token
                b.git_url = git_url
                b.code_path = code_path
                b.sql_path = sql_path
                b.mod = mod
            b.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '添加/更新子模块编译工程发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '添加/更新子模块编译工程成功'}))

    @staticmethod
    def load_buildjob_info(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'mid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定子模块'}))
        try:
            mid = int(request.GET.get('mid'))
            module = Prod_Module.objects.get(id=mid)
            b = Prod_BuildJobs.objects.filter(module=module)
            if len(b) < 1:
                return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': {'build': 'false'}}))
            else:
                b = b[0]
                buildinfo = {'jenkins': b.jenkins.id, 'job_name': b.job_name, 'token': b.token, 'git_url': b.git_url,
                             'code_path': b.code_path, 'sql_path': b.sql_path}
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取子模块编译工程信息发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': {'build': 'true', 'buildinfo': buildinfo}}))

    @staticmethod
    def disable_action(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'aid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定部署命令'}))
        try:
            aid = int(request.GET.get('aid'))
            action = Dep_Action.objects.get(id=aid)
            if action.active == 'Y':
                action.active = 'N'
            else:
                action.active = 'Y'
            action.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '启用/禁用部署命令发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': action.active}))

    @staticmethod
    def disable_test(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'tid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定自动测试工程'}))
        try:
            tid = int(request.GET.get('tid'))
            testjob = Prod_TestJob.objects.get(id=tid)
            if testjob.active == 'Y':
                testjob.active = 'N'
            else:
                testjob.active = 'Y'
            testjob.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '启用/禁用自动测试工程发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': testjob.active}))

    @staticmethod
    def rm_test(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'tid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定自动测试工程'}))
        try:
            tid = int(request.GET.get('tid'))
            testjob = Prod_TestJob.objects.get(id=tid)
            name = testjob.name
            params = testjob.params.all()
            for param in params:
                param.delete()
            testjob.delete()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '删除自动测试工程发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '自动测试工程 ' + name + ' 删除成功'}))

    @staticmethod
    def get_test_detail(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'tid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定自动测试工程'}))
        try:
            tid = int(request.GET.get('tid'))
            t = Prod_TestJob.objects.get(id=tid, vid=0)
            params = []
            p_s = t.params.all()
            for p in p_s:
                params.append({'id': p.id, 'key': p.key, 'value': p.value})
            detail = {'id': tid, 'name': t.name, 'pid': t.prod.id, 'vid': t.vid, 'sid': t.server.id,
                      'jid': t.jenkins.id, 'job_name': t.job_name, 'token': t.token, 'active': t.active,
                      'params': params}
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取自动测试工程详情发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': detail}))

    @staticmethod
    def edit_test(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'pid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定项目'}))
        if 'sid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定服务器'}))
        try:
            pid = int(request.GET.get('pid'))
            sid = int(request.GET.get('sid'))
            tid = int(request.POST.get('tid'))
            jid = int(request.POST.get('jid'))
            name = request.POST.get('name')
            job_name = request.POST.get('job_name')
            token = request.POST.get('token')
            params = json.loads(request.POST.get('params'))
            prod = Product.objects.get(id=pid)
            server = Dep_Server.objects.get(id=sid)
            jenkins = Prod_Jenkins.objects.get(id=jid)
            if tid == 0:
                t = Prod_TestJob(name=name, prod=prod, vid=0, server=server, jenkins=jenkins, job_name=job_name,
                                 token=token, active='Y')
            else:
                t = Prod_TestJob.objects.get(id=tid)
                t.name = name
                t.job_name = job_name
                t.token = token
                t.jenkins = jenkins
            t.save()
            del_list = []
            old_params = t.params.all()
            for o_p in old_params:
                del_list.append(o_p.id)
            for param in params:
                if param['pid'] == '0':
                    p = Prod_TestJob_Param(testjob=t, key=param['key'], value=param['value'])
                else:
                    p = Prod_TestJob_Param.objects.get(id=int(param['pid']))
                    p.key = param['key']
                    p.value = param['value']
                    del_list.remove(int(param['pid']))
                p.save()
            for d_p in del_list:
                p = Prod_TestJob_Param.objects.get(id=d_p)
                p.delete()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取自动测试工程详情发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (
        True, json.JSONEncoder().encode({'status': 'OK', 'msg': {'id': t.id, 'name': t.name, 'active': t.active}}))

    @staticmethod
    def edit_action(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'pid' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定产品'}))
        if 's' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定项目服务器'}))
        try:
            pid = int(request.GET.get('pid'))
            sid = int(request.GET.get('s'))
            if 'h' in request.GET:
                hid = int(request.GET.get('h'))
            else:
                hid = 0
            action_list = json.loads(request.POST.get('action_list'))
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '修改部署命令参数异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        try:
            old_actions = Dep_Action.objects.filter(server_id=sid, host_id=hid, prod_id=pid)
            o_actions = []
            for a in old_actions:
                o_actions.append(a.id)
            sequence = 0
            for a in action_list:
                sequence += 1
                aid = int(a['aid'])
                if aid != 0 and aid not in o_actions:
                    aid = 0
                if aid == 0:
                    new_action = Dep_Action(server_id=sid, host_id=hid, prod_id=pid, sequence=sequence,
                                            operation=a['operation'], param1=a['param1'], param2=a['param2'],
                                            param3=a['param3'], \
                                            param4=a['param4'], param5=a['param5'], active=a['active'])
                    new_action.save()
                else:
                    action = Dep_Action.objects.get(id=aid)
                    action.sequence = sequence
                    action.operation = a['operation']
                    action.param1 = a['param1']
                    action.param2 = a['param2']
                    action.param3 = a['param3']
                    action.param4 = a['param4']
                    action.param5 = a['param5']
                    action.active = a['active']
                    action.save()
                    o_actions.remove(aid)
            for aid in o_actions:
                d_action = Dep_Action.objects.get(id=aid)
                d_action.delete()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '修改部署命令发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '部署命令修改成功'}))

    @staticmethod
    def exec_shell(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'login' in request.session and request.session['login']:
            if 'uid' in request.session:
                uid = request.session['uid']
        request = json.loads(request.POST.get('request'))
        hid = request['hid']
        shell = request['shell']
        if shell.find('tomcat') == -1:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '只能操作tomcat下文件'}))
        elif shell.find(';') > -1:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '只能执行单条命令'}))
        else:
            try:
                auth = Auth.objects.get(id=int(uid))
                dh = Dep_Host.objects.get(id=int(hid))
                ssh = SSHHelper(hostname=dh.host, port=int(dh.ssh_port), username=dh.ssh_user, password=dh.ssh_pass,
                                key_file=dh.ssh_file)
                outputs, errs = ssh.run_command(shell)
                if len(errs) == 0:
                    ues = User_Exec_Shell(user=auth, host=dh, shell=shell)
                    ues.save()
                else:
                    return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': str(errs)}))
            except Exception as e:
                return (False, json.JSONEncoder().encode(
                    {'status': 'FAILED', 'msg': '执行失败: \n' + str(e) + '\n' + traceback.format_exc()}))
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': "执行成功"}))


