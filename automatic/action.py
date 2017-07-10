import json
import traceback
import automatic.utils.login as LOGIN
import automatic.utils.test as Test
import conf

from .utils.authentication import Authentication
from .utils.build import Build
from .utils.log import LOG
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .pages.build import BUILD_PAGE
from .pages.configuration import CONFIG_PAGE
from .pages.deploy import DEPLOY_PAGE
from .pages.execdb import EXECDB_PAGE
from .pages.manage import MANAGE_PAGE
from .pages.server import SERVER_PAGE
from .pages.test import TEST_PAGE
from .pages.user import USER_PAGE


def generate_request_log(request):
    log = {
        'scheme': request.scheme,
        'path': request.path,
        'method': request.method,
        'get': request.GET.dict(),
    }
    # if request.method == 'POST':
    # log['post'] = request.POST.dict()
    return json.JSONEncoder().encode(log)


# Most request that need to modify data in DB in 'action' category.
@csrf_exempt
def action(request):
    response = 'test'
    if 'a' in request.GET:
        action = request.GET.get('a')
        log = LOG(module='action', console=False)
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
        # EXECDB_PAGE: DB Creation
        if action == 'dbc':
            type = 'DBC'
            if auth.verify_action(type, action):
                lid = log.action(action='创建数据库', message=generate_request_log(request), uid=uid)
                status, r = EXECDB_PAGE.create_db(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        # EXECDB_PAGE: Add new database host in DB Creation page
        elif action == 'ndb':
            type = 'DBC'
            if auth.verify_action(type, action):
                lid = log.action(action='添加数据库主机', message=generate_request_log(request), uid=uid)
                status, r = EXECDB_PAGE.new_db_host(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #EXECDB_PAGE: Remove DB host
        elif action == 'ddh':
            type = 'DBC'
            if auth.verify_action(type, action):
                lid = log.action(action='删除数据库主机', message=generate_request_log(request), uid=uid)
                status, r = EXECDB_PAGE.del_db_host(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #EXECDB_PAGE: Get server list and DB list
        elif action == 'gsd':
            type = 'DBC'
            if auth.verify_action(type, action):
                status, r = EXECDB_PAGE.get_servers_dbs(request)
                response = r
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #Edit Server
        elif action == 'eds':
            type = 'SERVER'
            if auth.verify_action(type, action):
                lid = log.action(action='修改项目', message=generate_request_log(request), uid=uid)
                status, r = SERVER_PAGE.edit_server(request)
                response = get_basic_response(action, status, r)
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #SERVER_PAGE: Disable server
        elif action == 'dis':
            type = 'SERVER'
            if auth.verify_action(type, action):
                lid = log.action(action='禁用项目', message=generate_request_log(request), uid=uid)
                status, r = SERVER_PAGE.disable_server(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #SERVER_PAGE: Delete server
        elif action == 'des':
            type = 'SERVER'
            if auth.verify_action(type, action):
                lid = log.action(action='删除项目', message=generate_request_log(request), uid=uid)
                status, r = SERVER_PAGE.delete_server(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #SERVER_PAGE: Load page
        elif action == 'sld':
            type = 'SERVER'
            if auth.verify_action(type, action):
                status, r = SERVER_PAGE.load_page(request)
                response = r
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #SERVER_PAGE: Set server to production or not
        elif action == 'ssp':
            type = 'SERVER'
            if auth.verify_action(type, 'eds'):
                lid = log.action(action='设置环境是否为生产环境', message=generate_request_log(request), uid=uid)
                status, r = SERVER_PAGE.set_server_production(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #CONFIG_PAGE: Get prod and module list in Configuration page
        elif action == 'ldc':
            type = 'CONFIG'
            if auth.verify_action(type, action):
                status, r = CONFIG_PAGE.load_data(request)
                response = r
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #CONFIG_PAGE: Edit configure file
        elif action == 'set':
            type = 'CONFIG'
            if auth.verify_action(type, action):
                lid = log.action(action='修改配置文件', message=generate_request_log(request), uid=uid)
                status, r = CONFIG_PAGE.edit_config(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #CONFIG_PAGE: Delete config file
        elif action == 'rmc':
            type = 'CONFIG'
            if auth.verify_action(type, action):
                lid = log.action(action='取消关联', message=generate_request_log(request), uid=uid)
                status, r = CONFIG_PAGE.disrelation(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #New Configuration File
        elif action == 'ncf':
            type = 'CONFIG'
            if auth.verify_action(type, action):
                lid = log.action(action='配置关联', message=generate_request_log(request), uid=uid)
                status, r = CONFIG_PAGE.create_relation(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        elif action == 'crc':
            type = 'CONFIG'
            if auth.verify_action(type, action):
                lid = log.action(action='读取配置', message=generate_request_log(request), uid=uid)
                status, r = CONFIG_PAGE.read_conf(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #Deploy
        elif action == 'dep':
            type = 'DEPLOY'
            if auth.verify_action(type, action):
                lid = log.action(action='部署', message=generate_request_log(request), uid=uid)
                status, r = DEPLOY_PAGE.deploy(request)
                response = get_basic_response(action, status, r)
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #DEPLOY_PAGE: Trigger one test
        elif action == 'tst':
            type = 'TEST'
            if auth.verify_action(type, 'tst'):
                lid = log.action(action='触发自动测试', message=generate_request_log(request), type='test', uid=uid)
                status, r = DEPLOY_PAGE.trigger_test(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #DEPLOY_PAGE: Trigger all test
        elif action == 'tat':
            type = 'TEST'
            if auth.verify_action(type, 'tst'):
                lid = log.action(action='触发全部自动测试', message=generate_request_log(request), type='test', uid=uid)
                status, r = DEPLOY_PAGE.trigger_all_tests(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Add/Update product
        elif action == 'aup':
            type = 'MANAGE'
            if auth.verify_action(type, action):
                lid = log.action(action='添加/更新产品信息', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.add_prod(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Disable/Enable product
        elif action == 'dip':
            type = 'MANAGE'
            if auth.verify_action(type, action):
                lid = log.action(action='启用/禁用产品', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.disable_prod(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Add module to product
        elif action == 'adm':
            type = 'MANAGE'
            if auth.verify_action(type, action):
                lid = log.action(action='添加子模块', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.add_module(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Edit module
        elif action == 'edm':
            type = 'MANAGE'
            if auth.verify_action(type, action):
                lid = log.action(action='更新子模块信息', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.edit_module(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Disable/Enable module
        elif action == 'dim':
            type = 'MANAGE'
            if auth.verify_action(type, action):
                lid = log.action(action='启用/禁用子模块', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.disable_module(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Remove module
        elif action == 'rmm':
            type = 'MANAGE'
            if auth.verify_action(type, action):
                lid = log.action(action='删除子模块', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.rm_module(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Remove_product
        elif action == 'rmp':
            type = 'MANAGE'
            if auth.verify_action(type, action):
                lid = log.action(action='删除产品', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.rm_product(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Add/Edit module's build job
        elif action == 'amb':
            type = 'MANAGE'
            if auth.verify_action(type, action):
                lid = log.action(action='添加/更新子模块编译工程', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.edit_buildjob(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Add/Edit module's build job
        elif action == 'esh':
            type = 'MANAGE'
            if auth.verify_action(type, action):
                lid = log.action(action='执行shell命令', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.exec_shell(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Disable/Enable deploy action
        elif action == 'dia':
            type = 'DEPLOY'
            if auth.verify_action(type, action):
                lid = log.action(action='添加/更新子模块编译工程', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.disable_action(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Edit deploy action
        elif action == 'eda':
            type = 'DEPLOY'
            if auth.verify_action(type, action):
                lid = log.action(action='添加/更新子模块编译工程', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.edit_action(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Load page data
        elif action == 'ldm':
            type = 'MANAGE'
            if auth.verify_action(type, action):
                status, r = MANAGE_PAGE.load_data(request)
                response = r
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Disable/Enable test job
        elif action == 'dit':
            type = 'TEST'
            if auth.verify_action(type, action):
                lid = log.action(action='启/禁用自动测试工程', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.disable_test(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Delete test job
        elif action == 'rmt':
            type = 'TEST'
            if auth.verify_action(type, action):
                lid = log.action(action='删除自动测试工程', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.rm_test(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Get test job detail
        elif action == 'gtd':
            type = 'TEST'
            if auth.verify_action(type, action):
                status, r = MANAGE_PAGE.get_test_detail(request)
                response = r
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #MANAGE_PAGE: Add/Edit test job
        elif action == 'edt':
            type = 'TEST'
            if auth.verify_action(type, action):
                lid = log.action(action='添加/修改自动测试工程', message=generate_request_log(request), uid=uid)
                status, r = MANAGE_PAGE.edit_test(request)
                response = r
                action_done(log, lid, status, r)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
    return HttpResponse(response)


# User/Permission related operations
@csrf_exempt
def user(request):
    r = 'OK'
    if 'a' in request.GET:
        action = request.GET.get('a')
        log = LOG(module='action', console=False)
        type = 'USER'
        uid = conf.USER_ANONYMOUS
        if 'login' in request.session.keys() and request.session['login']:
            if 'uid' in request.session.keys():
                uid = request.session['uid']
            else:
                request.session['login'] = False
                request.session['uid'] = conf.USER_ANONYMOUS
                request.session['user'] = conf.USER_ANONYMOUS_NAME
        if uid == conf.USER_ANONYMOUS and action not in ['rep', 'snp']:
            return HttpResponse(
                json.JSONEncoder().encode({'status': 'OK', 'msg': {'user_info': {}, 'user_permissions': []}}))
        # USER_PAGE: Load USER_PAGE data
        if action == 'lda':
            lid = log.action(action='浏览用户信息页面', message=generate_request_log(request), type='user', uid=uid)
            status, r = USER_PAGE.load_data(request)
            action_done(log, lid, status, r)
        #USER_PAGE: Disable/Enable user
        elif action == 'diu':
            lid = log.action(action='启/禁用用户', message=generate_request_log(request), type='user', uid=uid)
            if uid != conf.USER_ADMIN:
                status = False
                r = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
            else:
                status, r = USER_PAGE.disable_user(request)
            action_done(log, lid, status, r)
        #USER_PAGE: Delete user
        elif action == 'rmu':
            lid = log.action(action='删除用户', message=generate_request_log(request), type='user', uid=uid)
            if uid != conf.USER_ADMIN:
                status = False
                r = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
            else:
                status, r = USER_PAGE.rm_user(request)
            action_done(log, lid, status, r)
        #USER_PAGE: Update user permission
        elif action == 'uup':
            lid = log.action(action='更新用户权限', message=generate_request_log(request), type='user', uid=uid)
            if uid != conf.USER_ADMIN:
                status = False
                r = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
            else:
                status, r = USER_PAGE.update_user_permit(request)
            action_done(log, lid, status, r)
        #USER_PAGE: Update user information
        elif action == 'uui':
            lid = log.action(action='更新用户信息', message=generate_request_log(request), type='user', uid=uid)
            status, r = USER_PAGE.update_userinfo(request)
            action_done(log, lid, status, r)
        #USER_PAGE: Update user email subscribe list
        elif action == 'ups':
            lid = log.action(action='更新用户产品/环境邮件列表', message=generate_request_log(request), type='user', uid=uid)
            status, r = USER_PAGE.update_subscribe(request)
            action_done(log, lid, status, r)
        #USER_PAGE: Apply reset user password
        elif action == 'rep':
            lid = log.action(action='申请重置用户密码', message=generate_request_log(request), type='user', uid=uid)
            status, r = USER_PAGE.apply_reset_pass(request)
            action_done(log, lid, status, r)
        #USER_PAGE: Reset user password
        elif action == 'snp':
            lid = log.action(action='显示重置用户密码页面', message=generate_request_log(request), type='user', uid=uid)
            status, r = USER_PAGE.show_reset_pass(request)
            action_done(log, lid, status, r)
        #USER_PAGE: Reset user password finish
        elif action == 'rpf':
            lid = log.action(action='重置用户密码', message=generate_request_log(request), type='user', uid=uid)
            status, r = USER_PAGE.reset_pass(request)
            action_done(log, lid, status, r)
    return HttpResponse(r)


# View/Read non-critical data
@csrf_exempt
def view(request):
    response = 'OK'
    if 'a' in request.GET:
        action = request.GET.get('a')
        #Get product list in build page
        if action == 'gpb':
            status, response = BUILD_PAGE.get_prods(request)
        #Get product branch build list in build page
        elif action == 'gbu':
            status, response = BUILD_PAGE.get_builds(request)
        #Load page in build page
        elif action == 'lop':
            status, response = BUILD_PAGE.load_page(request)
        #Get build details
        elif action == 'gbd':
            status, response = BUILD_PAGE.get_build_detail(request)
        #Get build deployed server list
        elif action == 'bds':
            status, response = BUILD_PAGE.get_build_servers(request)
        #Get build_details
        elif action == 'bdd':
            status, response = BUILD_PAGE.build_details(request)
        #Get Product List
        elif action == 'gpl':
            status, response = DEPLOY_PAGE.get_prod_info(request)
        #DEPLOY_PAGE: Load deploy history
        elif action == 'ldh':
            status, response = DEPLOY_PAGE.load_history(request)
        #DEPLOY_PAGE: Load deploy history detail
        elif action == 'ldd':
            status, response = DEPLOY_PAGE.load_history_detail(request)
        #Update deploy page
        elif action == 'upd':
            status, response = DEPLOY_PAGE.get_server_list(request)
        #Deploy log
        elif action == 'dpl':
            status, response = DEPLOY_PAGE.get_log(request)
        #DEPLOY_PAGE: Get server test detail list
        elif action == 'gts':
            status, response = DEPLOY_PAGE.get_test_detail(request)
        #MANAGE_PAGE: Load buildjob info
        elif action == 'gbi':
            status, response = MANAGE_PAGE.load_buildjob_info(request)
        elif action == 'gst':
            status, response = TEST_PAGE.get_script_task(request)
    return HttpResponse(response)


#Auto test status update
@csrf_exempt
def test(request):
    response = 'OK'
    if 'a' in request.GET:
        action = request.GET.get('a')
        #Test start
        if action == 'start':
            status, response = Test.test_start(request)
        #Test finished with no Jenkins error
        elif action == 'end':
            status, response = Test.test_end(request)
        #Test finished with Jenkins job failed
        elif action == 'failed':
            status, response = Test.test_failed(request)
    return HttpResponse(response)


#Build related actions and status update
@csrf_exempt
def build(request):
    response = 'OK'
    if 'a' in request.GET:
        action = request.GET.get('a')
        log = LOG(module='action', console=False)
        uid = conf.USER_ANONYMOUS
        if 'login' in request.session.keys() and request.session['login']:
            if 'uid' in request.session.keys():
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
        #Checkout code
        if action == 'cko':
            status, response = Build.bj_checkout(request)
        elif action == 'start':
            status, response = Build.bj_start(request)
        elif action == 'end':
            status, response = Build.bj_end(request)
        elif action == 'failed':
            status, response = Build.bj_failed(request)
        #Make build
        elif action == 'mkb':
            type = 'BUILD'
            if auth.verify_action(type, action):
                lid = log.action(action='编译新版本', message=generate_request_log(request), type='build', uid=uid)
                status, response = make_build(request)
                action_done(log, lid, status, response)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #Add branch
        elif action == 'adb':
            type = 'BUILD'
            if auth.verify_action(type, action):
                lid = log.action(action='添加新分支', message=generate_request_log(request), uid=uid)
                status, response = Build.add_branch(request)
                action_done(log, lid, status, response)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
        #BUILD_PAGE: Certify build manually
        elif action == 'ctb':
            type = 'BUILD'
            if auth.verify_action(type, action):
                lid = log.action(action='手动认证版本质量', message=generate_request_log(request), uid=uid)
                status, response = BUILD_PAGE.certify_build(request)
                action_done(log, lid, status, response)
            else:
                response = json.JSONEncoder().encode({'status': 'FAILED', 'msg': '没有执行权限'})
    return HttpResponse(response)


#Login actions
@csrf_exempt
def login(request):
    response = 'OK'
    if 'a' in request.GET:
        action = request.GET.get('a')
        log = LOG(module='login', console=False)
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
        if action == 'log':
            lid = log.action(action='用户登录', message=generate_request_log(request), type='login', uid=uid)
            status, response = LOGIN.login(request)
            action_done(log, lid, status, response)
        elif action == 'nwu':
            lid = log.action(action='用户注册', message=generate_request_log(request), type='login', uid=uid)
            status, response = LOGIN.new_user(request)
            action_done(log, lid, status, response)
        elif action == 'lot':
            lid = log.action(action='用户退出', message=generate_request_log(request), type='login', uid=uid)
            status, response = LOGIN.logout(request)
            action_done(log, lid, status, response)
    return HttpResponse(response)


#Finish log, to store function status in log system
def action_done(log, lid, status, result):
    if status:
        s = 'D'
    elif not status:
        s = 'F'
    elif status is None:
        s = 'N'
    else:
        s = 'O'
        result = status + '  @  ' + result
    return log.done(lid, s, result)


def get_basic_response(action=None, status=None, r=None):
    if action is None or status is None:
        return 'test'
    i = 1
    if status:
        i = 0
    response = conf.basic_response[action][i]
    if r is not None and len(r) > 1:
        response = r
    return response


#Trigger build making
def make_build(request):
    if request is None:
        return (False, 'HTTP request失效')
    pid = None
    bid = None
    if 'pid' in request.GET:
        pid = request.GET.get('pid')
        try:
            pid = int(pid)
        except ValueError as e:
            print("Build Product ID convert error: \n" + str(e) + '\n' + traceback.format_exc())
    if 'bid' in request.GET:
        bid = request.GET.get('bid')
        try:
            bid = int(bid)
        except ValueError as e:
            print("Build Branch ID convert error: \n" + str(e) + '\n' + traceback.format_exc())
    if pid is None or bid is None or pid < 1 or bid < 1:
        return (False, 'Build failed due to product ID or branch ID error.')
    desc = 'new build'
    if 'desc' in request.POST:
        desc = request.POST.get('desc')
    modules = None
    if 'modules' in request.POST:
        modules = json.loads(request.POST.get('modules'))
    build_master = conf.USER_DEFAULT
    if 'u' in request.GET:
        try:
            build_master = int(request.GET.get('u'))
        except ValueError as e:
            pass
    try:
        build = Build(prod_id=pid, branch_id=bid, build_master=build_master, descript=desc)
        build.new_build(modules)
    except Exception as e:
        response = {'status': 'Failed', 'msg': str(e) + '\n' + traceback.format_exc()}
    else:
        response = {'status': 'OK', 'msg': ''}
    response = json.JSONEncoder().encode(response)
    return (True, response)
