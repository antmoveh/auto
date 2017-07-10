import datetime
import json
import threading
import traceback
import automatic.utils.test as Test
import automatic.utils.product as PROD
import conf

from automatic.utils.authentication import Authentication
from django.shortcuts import render_to_response
from automatic.models import *
from .test import TEST_PAGE
from .webpage import WEBPAGE
from automatic.tools.deploy import DEPLOY


class DEPLOY_PAGE(WEBPAGE):
    template = 'pages/deploy.html'

    def __init__(self, request, type=None):
        super().__init__(request, type)

    def render(self, request):
        title, tab_list = self.generate_nav_tabs(self.type)
        uid, username, login = self.render_user(request)
        return render_to_response(self.template,
                                  {'title': title, 'tabs': tab_list, 'login': login, 'uid': uid, 'username': username})

    @staticmethod
    def get_server_list(request):
        if request is None:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'})
        try:
            page = int(request.GET.get("p"))
        except:
            page = 1
        try:
            prods = {}
            group_id = Authentication.verify_group(request)
            if group_id == 0:
                return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '获取产品信息出错'})
            elif group_id == 1:
                all_prod = Product.objects.all()
                all_server = Dep_Server.objects.filter(active='Y').order_by("-id")
            else:
                all_prod = Product.objects.filter(group_id=group_id)
                all_server = Dep_Server.objects.filter(active='Y', group_id=group_id).order_by("-id")
            for prod in all_prod:
                prods[prod.id] = prod.name
            onsites = {}
            onsite_vids = []
            dep_users = []
            all_onsite = Dep_Status.objects.filter(on_server='Y')
            for onsite in all_onsite:
                onsites[onsite.server.id] = [onsite.prod, onsite.version, onsite.dep_user, onsite.dep_time,
                                             onsite.dep_status]
            server_list = []
            count = len(all_server)
            #获取前二十条
            if page is not None:
                step = conf.PAGE_STEP
                start = (page - 1) * step
                end = start + step
                all_server = all_server[start:end]
            for server in all_server:
                if server.id not in onsites:
                    info = {'id': server.id, 'name': server.server, 'production': server.production, 'version': 'N/A',
                            'time': 'N/A', 'user': 'N/A', 'status': 'N/A', 'count': count}
                    server_list.append(info)
                else:
                    on_s = onsites[server.id]
                    p_name = on_s[0].name
                    p_ver = on_s[1].version
                    dep_user = on_s[2].display
                    tz_diff = datetime.timedelta(hours=8)
                    dep_time = str(on_s[3] + tz_diff)
                    status = on_s[4]
                    info = {'id': server.id, 'name': server.server, 'production': server.production,
                            'version': p_name + ' ' + p_ver, 'time': dep_time, 'user': dep_user, 'status': status,
                            'count': count}
                    server_list.append(info)
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取部署服务器信息列表发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return True, json.JSONEncoder().encode({'status': 'OK', 'msg': server_list})

    @staticmethod
    def get_prod_info(request):
        if request is None:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'})
        if 's' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定项目服务器'})
        try:
            sid = int(request.GET.get('s'))
            server = Dep_Server.objects.get(id=sid)
            verified = False
            if server.production == 'Y':
                verified = True
            dep = Dep_Status.objects.filter(server=server, on_server='Y')
            pid = None
            bid = None
            vid = None
            if len(dep) > 0:
                pid = dep[0].prod_id
                bid = dep[0].branch.id
                vid = dep[0].version_id
            prod_list = PROD.get_products(pid)
            ver_list = {}
            for prod in prod_list:
                p_id = prod[0]
                b_id = None
                v_id = None
                if pid == p_id:
                    b_id = bid
                    v_id = vid
                ver_list[str(prod[0])] = PROD.get_deploy_builds(p_id=p_id, bid=b_id, v_id=v_id, verified=verified)
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取部署产品信息发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return (
        True, json.JSONEncoder().encode({'status': 'OK', 'msg': {'prod_list': prod_list, 'ver_list': ver_list}}))

    @staticmethod
    def deploy(request):
        if request is None:
            return False, 'HTTP request失效'
        if 'sid' not in request.POST:
            return False, '未指定要进行部署的服务器'
        if 'pid' not in request.POST:
            return False, '未指定要部署的产品'
        if 'vid' not in request.POST:
            return False, '未指定要部署的版本'
        if 'uid' not in request.POST:
            return False, '未知部署账号'
        sid = request.POST.get('sid')
        pid = request.POST.get('pid')
        bid = request.POST.get('bid')
        vid = request.POST.get('vid')
        uid = request.POST.get('uid')
        server = Dep_Server.objects.filter(id=int(sid))
        if len(server) == 1:
            server = server[0]
        else:
            return False, '无法找到指定要进行部署的服务器'
        user = Auth.objects.filter(id=int(uid))
        if len(user) == 1:
            user = user[0]
        else:
            return False, '无法找到指定要进行部署的用户'
        prod = PROD.get_product(int(pid))
        if prod is None:
            return False, '无法找到指定要进行部署的产品'
        branch = PROD.get_branch(bid)
        if branch is None:
            return False, '无法找到指定要进行部署的版本'
        ver = PROD.get_version(vid)
        if ver is None:
            return False, '无法找到指定要进行部署的编译版本'
        t = threading.Thread(target=DEPLOY_PAGE.deploy_thread, kwargs={
        'sid': server.id,
        's_name': server.server,
        'pid': int(pid),
        'prod': prod,
        'bid': bid,
        'branch': branch['branch'],
        'vid': ver['id'],
        'version': ver['version'],
        'uid': int(uid),
        'username': user.username})
        t.start()
        return True, json.JSONEncoder().encode({'status': 'OK', 'msg': '已开始部署'})

    @staticmethod
    def deploy_thread(sid, s_name, pid, prod, bid, branch, vid, version, uid, username):
        product = Product.objects.get(id=int(pid))
        server = Dep_Server.objects.get(id=int(sid))
        dep = DEPLOY(s_id=sid, s_name=s_name)
        dep.set_prod(pid=int(pid), prod=prod, bid=bid, branch=branch, vid=vid, version=version)
        dep.set_user(uid=int(uid), username=username)
        status = dep.deploy()
        dep.send_deploy_email()
        if status:
            TEST_PAGE.start_test(server, product)
        #	tests = Prod_TestJob.objects.filter(prod = product, vid = 0, server = server, active = 'Y')
        #	for test in tests:
        #		Test.new_test(test.id)

    @staticmethod
    def get_log(request):
        if 'sid' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定服务器'})
        sid = int(request.GET.get('sid'))
        server = Dep_Server.objects.filter(id=sid)
        if len(server) > 0:
            server = server[0]
        deploy = Dep_Status.objects.filter(server=server, on_server='Y')
        if len(deploy) > 0:
            deploy = deploy[0]
        else:
            return False, json.JSONEncoder().encode({'status': 'None'})
        iid = deploy.id
        pid = deploy.prod.id
        vid = deploy.version.id
        uid = deploy.dep_user.id
        tz_diff = datetime.timedelta(hours=8)
        dep_time = str(deploy.dep_time + tz_diff)
        desc = deploy.description
        status = deploy.dep_status
        if status == 'D':
            status = '部署中...'
        elif status == 'Y':
            status = '部署成功'
        elif status == 'F':
            status = '部署失败'
        elif status == 'T':
            staus = '测试中...'
        sname = server.server
        prod = Product.objects.filter(id=pid)
        if len(prod) > 0:
            prod = prod[0]
        pname = prod.name
        version = Prod_Version.objects.filter(id=vid)
        if len(version) > 0:
            version = version[0]
        ver = version.version
        user = Auth.objects.filter(id=uid)
        if len(user) > 0:
            user = user[0]
        uname = user.display
        log_list = []
        logs = Dep_Log.objects.filter(iid=iid)
        if len(logs) > 0:
            for log in logs:
                log_list.append([str(log.time + tz_diff), log.status, log.detail])
        deploy_log = {
        'server': sname,
        'product': pname,
        'version': ver,
        'time': dep_time,
        'user': uname,
        'desc': desc,
        'status': status,
        'logs': log_list,
        }
        return True, json.JSONEncoder().encode({'status': 'OK', 'msg': deploy_log})

    @staticmethod
    def load_history(request):
        if 'sid' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定服务器'})
        try:
            sid = int(request.GET.get('sid'))
            history_list = []
            start = 0
            step = 20
            tz_diff = datetime.timedelta(hours=8)
            server = Dep_Server.objects.get(id=sid)
            d_h = Dep_Status.objects.filter(server=server).order_by('-id')[start: start + step]
            for d in d_h:
                history_list.append(
                    {'id': d.id, 'prod': d.prod.name, 'version': d.version.version, 'user': d.dep_user.display,
                     'time': str(d.dep_time + tz_diff), 'description': d.description, 'status': d.dep_status,
                     'on': d.on_server})
            response = {'server': server.server, 'history_list': history_list}
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取部署历史发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return True, json.JSONEncoder().encode({'status': 'OK', 'msg': response})

    @staticmethod
    def load_history_detail(request):
        if 'did' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定部署'})
        try:
            did = int(request.GET.get('did'))
            detail_list = Dep_Log.objects.filter(iid=did)
            details = []
            tz_diff = datetime.timedelta(hours=8)
            for detail in detail_list:
                details.append({'time': str(detail.time + tz_diff), 'status': detail.status, 'detail': detail.detail})
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取部署历史细节发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return True, json.JSONEncoder().encode({'status': 'OK', 'msg': details})

    @staticmethod
    def get_test_detail(request):
        if 'sid' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定服务器'})
        try:
            sid = int(request.GET.get('sid'))
            tz_diff = datetime.timedelta(hours=8)
            server = Dep_Server.objects.get(id=sid)
            tests = []
            deploy = Dep_Status.objects.filter(server=server, on_server='Y')
            if len(deploy) > 0:
                deploy = deploy.order_by('-id')[0]
                prod = deploy.prod
                testjobs = Prod_TestJob.objects.filter(prod=prod, server=server)
                for j in testjobs:
                    test = Prod_Test.objects.filter(prod=prod, testjob=j, server=server, deploy=deploy).order_by('-id')
                    time = 'N/A'
                    status = 'N'
                    url = ' disabled'
                    tid = '0'
                    if len(test) > 0:
                        test = test[0]
                        status = test.status
                        tid = str(test.id)
                        jenkins = j.jenkins.url
                        time = '开始: ' + str(test.start_time + tz_diff)
                        if status in ['Y', 'F']:
                            time += '<br>结束: ' + str(test.end_time + tz_diff)
                        if jenkins[-1] != '/':
                            jenkins += '/'
                        url = ' onclick=\"window.open(\'' + jenkins + 'job/' + j.job_name + '/' + test.b_id + '/console\');\"'
                    tests.append({'jid': str(j.id), 'name': j.name, 'tid': tid, 'status': status, 'detail_url': url,
                                  'time': time})
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取测试结果发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return True, json.JSONEncoder().encode({'status': 'OK', 'msg': tests})

    @staticmethod
    def trigger_test(request):
        if 'jid' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定服务器'})
        try:
            jid = int(request.GET.get('jid'))
            Test.new_test(jid)
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '触发测试工程发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return True, json.JSONEncoder().encode({'status': 'OK', 'msg': '测试已触发'})

    @staticmethod
    def trigger_all_tests(request):
        if 'tests' not in request.POST:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未提供测试工程列表'})
        try:
            tests = json.loads(request.POST.get('tests'))
            for test in tests:
                Test.new_test(int(test))
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '触发测试工程发生异常: \n' + str(e) + '\n' + traceback.format_exc()}))
        return True, json.JSONEncoder().encode({'status': 'OK', 'msg': '测试已触发'})
