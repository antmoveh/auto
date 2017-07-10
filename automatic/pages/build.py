import datetime
import json
import re
import traceback
import urllib.request
import automatic.utils.product as PROD
import conf

from automatic.utils.authentication import Authentication
from django.shortcuts import render_to_response
from automatic.models import *
from .webpage import WEBPAGE


class BUILD_PAGE(WEBPAGE):
    template = 'pages/build.html'

    def __init__(self, request, type=None):
        super().__init__(request, type)

    def render(self, request):
        title, tab_list = self.generate_nav_tabs(self.type)
        uid, username, login = self.render_user(request)
        return render_to_response(self.template,
                                  {'title': title, 'tabs': tab_list, 'login': login, 'uid': uid, 'username': username})

    @staticmethod
    def get_prods(request):
        if request is None:
            return False, 'HTTP request is None.'
        pid = None
        if 'pid' in request.GET:
            try:
                pid = int(request.GET.get('pid'))
            except ValueError as e:
                pass
        prod_list = PROD.get_products(pid)
        response = json.JSONEncoder().encode(prod_list)
        return True, response

    @staticmethod
    def get_page(p=None):
        page = 1
        if p is not None:
            try:
                page = int(p)
            except ValueError as e:
                pass
        if page < 1:
            page = 1
        return page

    @staticmethod
    def get_branchs(request):
        if request is None:
            return False, 'HTTP request is None.'
        if 'pid' not in request.GET:
            return False, 'Product ID is not provided.'
        pid = request.GET.get('pid')
        bid = None
        if 'bid' in request.GET:
            bid = request.GET.get('bid')
        current_branch, branch_list = PROD.get_branchs(int(pid), bid)
        build_list = []
        if current_branch is not None:
            page_start = 1
            if 'p' in request.GET:
                page_start = BUILD_PAGE.get_page(request.GET.get('p'))
            build_list = PROD.get_builds(int(pid), current_branch, start=(page_start - 1) * BUILD_PAGE.page_items,
                                         step=BUILD_PAGE.page_items)
        response = json.JSONEncoder().encode({'br_list': branch_list, 'bu_list': build_list})
        return True, response

    @staticmethod
    def get_builds(request):
        if request is None:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request is None.'})
        if 'pid' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定产品'})
        if 'bid' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定分支'})
        try:
            pid = int(request.GET.get('pid'))
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '产品错误: ' + str(e) + '\n' + traceback.format_exc()}))
        try:
            bid = int(request.GET.get('bid'))
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '分支错误: ' + str(e) + '\n' + traceback.format_exc()}))
        try:
            page = int(request.GET.get('p'))
        except:
            page = 1
        try:
            prod = Product.objects.get(id=pid)
            branch = Prod_Branch.objects.get(id=bid)
            count, build_list = BUILD_PAGE.get_branch_builds(branch, page)
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取版本信息发生异常: ' + str(e) + '\n' + traceback.format_exc()}))
        return (True, json.JSONEncoder().encode(
            {'status': 'OK', 'msg': {'count': count, 'builds': build_list, 'page_step': conf.PAGE_STEP}}))

    @staticmethod
    def get_branch_builds(branch, page=None):
        builds = []
        tz_diff = datetime.timedelta(hours=8)
        versions = branch.versions.all().order_by('-id')
        count = len(versions)
        if page is not None:
            step = conf.PAGE_STEP
            start = (page - 1) * step
            end = start + step
            versions = versions[start:end]
        for v in versions:
            builds.append({'id': v.id, 'version': v.version, 'build_master': v.build_master.display,
                           'time': str(v.build_time + tz_diff), 'status': v.status, 'certified': v.certified})
        return (count, builds)

    @staticmethod
    def load_page(request):
        if request is None:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request is None.'})
        try:
            pid = int(request.GET.get('pid'))
        except:
            pid = 0
        try:
            bid = int(request.GET.get('bid'))
        except:
            bid = 0
        try:
            page = BUILD_PAGE.get_page(request.GET.get('p'))
        except:
            page = 1
        try:
            prod_list = []
            module_list = []
            branch_list = []
            build_list = []
            count = 0
            group_id = Authentication.verify_group(request)
            if group_id == 0:
                return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '获取产品信息出错'})
            elif group_id == 1:
                prods = Product.objects.filter(active='Y')
            else:
                prods = Product.objects.filter(active='Y', group_id=group_id)
            for p in prods:
                selected = 0
                if pid == p.id:
                    selected = 1
                    modules = p.modules.filter(active='Y')
                    for module in modules:
                        module_list.append({'id': module.id, 'name': module.name})
                    branchs = p.branchs.all().order_by('-id')
                    for b in branchs:
                        if bid == 0:
                            bid = b.id
                        selected_branch = 0
                        if bid == b.id:
                            selected_branch = 1
                            count, build_list = BUILD_PAGE.get_branch_builds(b, page)
                        branch_list.append(
                            {'id': b.id, 'name': b.branch, 'git_branch': b.git_branch, 'selected': selected_branch})
                prod_list.append({'id': p.id, 'name': p.name, 'selected': selected})
            response = {'p_list': prod_list, 'br_list': branch_list, 'bu_list': build_list, 'module_list': module_list,
                        'bu_count': count, 'page_step': conf.PAGE_STEP, 'cbid': str(bid)}
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取产品信息列表失败: \n' + str(e) + '\n' + traceback.format_exc()}))
        return True, json.JSONEncoder().encode({'status': 'OK', 'msg': response})

    @staticmethod
    def get_build_detail(request):
        if request is None:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'})
        if 'bid' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定build'})
        vid = request.GET.get('bid')
        try:
            vid = int(vid)
        except ValueError as e:
            return (
                False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': str(e) + '\n' + traceback.format_exc()}))
        build = PROD.get_version(vid)
        if build is None:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未找到指定build'})
        else:
            build['build_master'] = build['build_master'].display
            return True, json.JSONEncoder().encode({'status': 'OK', 'msg': build})

    @staticmethod
    def get_build_servers(request):
        if request is None:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'})
        if 'bid' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定build'})
        try:
            vid = int(request.GET.get('bid'))
        except ValueError as e:
            return (
                False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': str(e) + '\n' + traceback.format_exc()}))
        servers = PROD.get_servers(vid)
        return True, json.JSONEncoder().encode({'status': 'OK', 'msg': servers})

    @staticmethod
    def certify_build(request):
        if request is None:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'})
        if 'bid' not in request.GET:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定build'})
        try:
            vid = int(request.GET.get('bid'))
        except ValueError as e:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '版本号ID错误'})
        try:
            version = Prod_Version.objects.get(id=vid)
            if version.certified == 'Y':
                version.certified = 'N'
            else:
                version.certified = 'Y'
            version.save()
        except Exception as e:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '认证版本质量发生异常: ' + str(e.args)})
        return True, json.JSONEncoder().encode({'status': 'OK', 'msg': version.certified})

    @staticmethod
    def build_details(requests):
        if requests is None:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'})
        try:
            url = requests.GET.get('url')
            response = str(urllib.request.urlopen(url).read())
            result = re.compile(r'<pre class="console-output">.*</pre>').findall(response)
            res = re.sub(r'\\n', '<br>', result[0])
        except Exception as e:
            return False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '获取编译详情发生异常: ' + str(e.args)})
        return True, json.JSONEncoder().encode({'status': 'OK', 'msg': res})

