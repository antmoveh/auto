import datetime
import os
import threading
import traceback
import automatic.utils.email as EMAIL
import automatic.utils.utils as UTILS

from .SSH import SSHHelper
from .config import Config
from .jenkins import *
from automatic.models import *


class Build():
    def __init__(self, prod_id, branch_id, modules=None, build_master=1, descript='new build'):
        try:
            prod = Product.objects.get(id=prod_id)
            branch = Prod_Branch.objects.get(id=branch_id)
            bm = Auth.objects.get(id=build_master)
        except Exception as e:
            raise Exception('初始化编译过程失败: \n' + str(e) + '\n' + traceback.format_exc())
        self.prod = prod
        self.branch = branch
        self.build_master = bm
        self.modules = modules
        self.descript = descript
        self.bsp_url = Config.get_config('env', 'bsp_url')['value']

    def get_buildnumber(self, last_v=None):
        try:
            v_b = self.branch.branch
            versions = self.branch.versions.all().order_by('-v_bn')
            if len(versions) > 0:
                v_bn = versions[0].v_bn + 1
            else:
                v_bn = 1
        except Exception as e:
            print('获取buildnumber出错: \n' + str(e) + '\n' + traceback.format_exc())
            v_bn = 1
            v_b = '1.1.1'
        return (v_b, v_bn)

    def get_module(self, mid=None):
        if mid is None:
            return ''
        try:
            module = Prod_Module.objects.get(id=mid)
        except Exception as e:
            return ''
        else:
            return module.name

    def __create_build(self, module, prod_v, v_b, version):
        prod_name = self.prod.name
        build_jobs = module.buildjobs.all()
        for b_j in build_jobs:
            build = Prod_Builds(prod=self.prod, v=prod_v, bj=b_j, q_id='-1', b_id='-1', status='W', rev='')
            build.save()
            b_id = build.id
            jenkins_server = b_j.jenkins
            jenkins = Jenkins(url=jenkins_server.url, username=jenkins_server.username,
                              password=jenkins_server.password)
            param = {'id': str(b_id), 'prod': prod_name, 'branch': v_b, 'buildnumber': version,
                     'module': b_j.module.name, 'bsp': self.bsp_url, 'git_branch': self.branch.git_branch}
            jenkins_q_id = jenkins.build_job(b_j.job_name, parameters=param, token=b_j.token)
            build.q_id = jenkins_q_id
            build.save()

    @staticmethod
    def cp_lastgood_builds(vid, builds):
        for b in builds:
            ssh = SSHHelper(hostname=b['host'], port=b['port'], username=b['user'], password=b['pass'],
                            key_file=b['key'])
            script = 'sudo mkdir -p ' + b['des_path'] + '; sudo cp \"' + b['src'] + '\" \"' + b[
                'des'] + '\"; sudo chown -R auto:auto \"' + b['des_ver'] + '\";'
            outputs, errs = ssh.run_command(script)
            if len(errs) > 0:
                print(str(errs))
                status = 'F'
            else:
                status = 'D'
            UTILS.close_db()
            b = Prod_Builds.objects.get(id=b['id'])
            b.status = status
            b.save()
        v = Prod_Version.objects.get(id=vid)
        Build.check_build_end(v)

    def __use_lastgood(self, module, lastgood, prod_v, v_b, version):
        storage = Config.get_config(type='env', name='storage')['value']
        if storage[-1] != '/':
            storage += '/'
        lastgood_path = lastgood.prod.name + '/' + lastgood.prod.name + '-' + lastgood.branch.branch + '/' + lastgood.prod.name + '-' + lastgood.version + '/' + module.name + '/'
        src_path = storage + lastgood_path
        build_jobs = module.buildjobs.all()
        marker = True
        builds = []
        for b_j in build_jobs:
            if b_j.mod == 'WAR' and os.path.isfile(src_path + b_j.job_name + '.war'):
                build = {}
                j = b_j.jenkins
                jenkins_storage = j.storage
                if jenkins_storage[-1] != '/':
                    jenkins_storage += '/'
                src = jenkins_storage + lastgood_path + b_j.job_name + '.war'
                des_ver = jenkins_storage + self.prod.name + '/' + self.prod.name + '-' + self.branch.branch + '/' + self.prod.name + '-' + version + '/'
                des_path = des_ver + module.name + '/'
                des = des_path + b_j.job_name + '.war'
                lastgood_b = lastgood.builds.get(bj=b_j)
                b = Prod_Builds(prod=self.prod, v=prod_v, bj=b_j, q_id=lastgood_b.q_id, b_id=lastgood_b.b_id,
                                status='B', rev=lastgood_b.rev)
                b.save()
                build = {'id': b.id, 'src': src, 'des_ver': des_ver, 'des_path': des_path, 'des': des, 'host': j.host,
                         'port': int(j.ssh_port), 'user': j.ssh_user, 'pass': j.ssh_pass, 'key': j.ssh_key}
                builds.append(build)
                marker = False
        if marker:
            print('Cannot find lastgood build package, creating new build.')
            self.__create_build(module=module, prod_v=prod_v, v_b=v_b, version=version)
        return builds

    def new_build(self, module_list=None):
        v_b, v_bn = self.get_buildnumber()
        version = v_b + '.' + str(v_bn)
        prod_v = Prod_Version(prod=self.prod, branch=self.branch, version=version, v_bn=v_bn, code_v='HEAD',
                              conf_v='HEAD', build_master=self.build_master,
                              build_time=datetime.datetime.now(), descript=self.descript, status='W', certified='N')
        prod_v.save()
        self.v_id = prod_v.id
        lastgood = Prod_Version.objects.filter(prod=self.prod, branch=self.branch, status='D').order_by('-id')
        if len(lastgood) > 0:
            lastgood = lastgood[0]
        else:
            lastgood = None
        modules = self.prod.modules.filter(active='Y')
        builds = []
        for module in modules:
            if module_list is not None and str(module.id) not in module_list and lastgood is not None:
                bs = self.__use_lastgood(module=module, lastgood=lastgood, prod_v=prod_v, v_b=v_b, version=version)
                builds.extend(bs)
            else:
                self.__create_build(module=module, prod_v=prod_v, v_b=v_b, version=version)
        if len(builds) > 0:
            t = threading.Thread(target=Build.cp_lastgood_builds, kwargs={'vid': prod_v.id, 'builds': builds})
            t.start()

    @staticmethod
    def bj_start(request):
        if request is None:
            return (False, 'HTTP request is None.')
        if 'id' in request.GET and 'rev' in request.GET:
            try:
                rev = request.GET.get('rev')
                build = Prod_Builds.objects.get(id=request.GET.get('id'))
                build.status = 'B'
                build.rev = rev
                build.save()
                v = build.v
                if v.status == 'O':
                    v.status = 'B'
                    v.save()
            except Exception as e:
                return (False, json.JSONEncoder().encode(
                    {'status': 'Failed', 'msg': 'Error: \n' + str(e) + '\n' + traceback.format_exc()}))
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': 'Build status updated: STARTED.'}))
        else:
            return (False, json.JSONEncoder().encode(
                {'status': 'Failed', 'msg': 'build ID or Jenkins build number is not provided.'}))

    @staticmethod
    def bj_checkout(request):
        if request is None:
            return (False, 'HTTP request is None.')
        if 'id' in request.GET and 'jid' in request.GET:
            try:
                build = Prod_Builds.objects.get(id=request.GET.get('id'))
                build.b_id = request.GET.get('jid')
                build.status = 'O'
                build.save()
                v = build.v
                if v.status == 'W':
                    v.status = 'O'
                    v.save()
            except Exception as e:
                return (False, json.JSONEncoder().encode(
                    {'status': 'Failed', 'msg': 'Error: \n' + str(e) + '\n' + traceback.format_exc()}))
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': 'Build status updated: CHECKOUT CODE.'}))
        else:
            return (False, json.JSONEncoder().encode(
                {'status': 'Failed', 'msg': 'build ID or Jenkins build number is not provided.'}))

    @staticmethod
    def bj_end(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': 'HTTP request is None.'}))
        if 'id' in request.GET:
            try:
                build = Prod_Builds.objects.get(id=request.GET.get('id'))
                build.status = 'D'
                build.save()
                v = build.v
                Build.check_build_end(v)
            except Exception as e:
                return (False, json.JSONEncoder().encode(
                    {'status': 'Failed', 'msg': 'Error: \n' + str(e) + '\n' + traceback.format_exc()}))
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': 'Build status updated: FINISHED.'}))
        else:
            return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': 'build ID is not provided.'}))

    @staticmethod
    def check_build_end(v):
        builds = v.builds.filter(status__in=['B', 'W'])
        if len(builds) < 1:
            if v.status not in ['F']:
                v.status = 'D'
                v.save()
            Build.send_mail(v.id)

    @staticmethod
    def bj_failed(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': 'HTTP request is None.'}))
        if 'id' in request.GET:
            try:
                build = Prod_Builds.objects.get(id=request.GET.get('id'))
                build.status = 'F'
                build.save()
                v = build.v
                v.status = 'F'
                v.save()
                Build.check_build_end(v)
            except Exception as e:
                return (False, json.JSONEncoder().encode(
                    {'status': 'Failed', 'msg': 'Error: \n' + str(e) + '\n' + traceback.format_exc()}))
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': 'Build status updated: FAILED.'}))
        else:
            return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': 'build ID is not provided.'}))

    @staticmethod
    def add_branch(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': '未收到客户端输入数据'}))
        if 'pid' in request.GET and 'b' in request.GET and 'u' in request.GET:
            try:
                pid = int(request.GET.get('pid'))
                u_id = int(request.GET.get('u'))
            except ValueError as e:
                return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': '产品ID类型应为整数'}))
            branch = request.GET.get('b')
            git_branch = request.GET.get('g_b')
            try:
                prod = Product.objects.get(id=pid)
                o_b = prod.branchs.filter(branch=branch)
                u = Auth.objects.get(id=u_id)
                if len(o_b) > 0:
                    return (False, json.JSONEncoder().encode(
                        {'status': 'Failed', 'msg': prod.name + '中版本 ' + branch + ' 已经存在'}))
                n_b = Prod_Branch(prod=prod, branch=branch, u=u, git_branch=git_branch, time=datetime.datetime.now())
                n_b.save()
            except Exception as e:
                return (False, json.JSONEncoder().encode(
                    {'status': 'Failed', 'msg': '添加新版本发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': prod.name + '添加新版本 ' + branch + ' 成功'}))
        else:
            return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': '未提供必要参数'}))

    @staticmethod
    def send_mail(vid):
        tz_diff = datetime.timedelta(hours=8)
        ver = Prod_Version.objects.get(id=vid)
        pid = ver.prod.id
        subscribes = User_Subscribe.objects.filter(prod_id__in=[0, pid], server_id=-1)
        cc = []
        for s in subscribes:
            cc.append(s.user.email)
        cc = list(set(cc))
        if ver.build_master.email in cc:
            cc.remove(ver.build_master.email)
        builds = ver.builds.all()
        if ver.status == 'D':
            v_s = '编译成功'
            v_s_t = '<font color=\"green\">编译成功</font>'
        elif ver.status == 'F':
            v_s = '编译失败'
            v_s_t = '<font color=\"red\"><b>编译失败</b></font>'
        else:
            v_s = ver.status
            v_s_t = ver.status
        build_list = []
        for build in builds:
            if build.status == 'D':
                b_s = '<font color=\"green\">成功</font>'
            elif build.status == 'F':
                b_s = '<font color=\"red\"><b>失败</b></font>'
            else:
                b_s = build.status
            jenkins = build.bj.jenkins.url
            if jenkins[-1] != '/':
                jenkins += '/'
            detail_url = jenkins + 'job/' + build.bj.job_name + '/' + build.b_id + '/console'
            build_list.append({'module': build.bj.module.name, 'rev': build.rev, 'status': b_s, 'detail': detail_url})
        build_detail = {
            'prod': ver.prod.name,
            'version': ver.version,
            'status': v_s,
            'status_t': v_s_t,
            'user': ver.build_master.display,
            'time': str(ver.build_time + tz_diff),
            'builds': build_list,
        }
        subject = ver.prod.name + ' ' + ver.version + ' ' + v_s
        EMAIL.mail(subject=subject, mode='build', html_context=build_detail, to_mail=[ver.build_master.email], cc=cc,
                   text_content=subject)
