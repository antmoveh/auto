import json
import traceback
import automatic.utils.sql as SQL
import conf

from subprocess import PIPE, Popen
from automatic.utils.authentication import Authentication
from automatic.utils.config import Config
from automatic.utils.exceptions import SQLError
from automatic.utils.log import LOG
from django.shortcuts import render_to_response
from automatic.models import *
from .webpage import WEBPAGE


class EXECDB_PAGE(WEBPAGE):
    template = 'pages/execdb.html'

    def __init__(self, request, type=None):
        super().__init__(request, type)

    def render(self, request):
        title, tab_list = self.generate_nav_tabs(self.type)
        uid, username, login = self.render_user(request)
        auth = Authentication(uid)
        add_server = False
        if auth.verify_action('DBC', 'ndb'):
            add_server = True
        return render_to_response(self.template,
                                  {'title': title, 'tabs': tab_list, 'login': login, 'uid': uid, 'username': username,
                                   'Add_Server': add_server})


    @staticmethod
    def new_db_host(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        j = json.loads(request.POST.get('request'))
        try:
            prod = Product.objects.get(id=int(j["server"]))
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取服务器信息失败：\n' + str(e) + '\n' + traceback.format_exc()}))
        try:
            name = j["name"]
            type = j["type"]
            db_host = j["db_host"]
            db_name = j["db_name"]
            db_port = j["db_port"]
            db_user = j["db_user"]
            db_pass = j["db_pass"]
            ndb_host = Dep_Sql(prod=prod, database=name, db_type=type, db_host=db_host, db_name=db_name,
                               db_port=db_port, db_user=db_user, db_pass=db_pass)
            ndb_host.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '添加数据库主机失败：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '数据库主机添加成功'}))

    @staticmethod
    def del_db_host(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        if 'did' not in request.GET:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '未指定要移除的数据库主机'}))
        try:
            did = int(request.GET.get('did'))
            dbh = Dep_Sql.objects.get(id=did)
            dbh.delete()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '移除数据库主机失败：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '数据库主机移除成功'}))

    @staticmethod
    def get_servers_dbs(request):
        prod_list = []
        db_list = {}
        try:
            group_id = Authentication.verify_group(request)
            if group_id == 0:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '获取服务信息出错'}))
            elif group_id == 1:
                prods = Product.objects.all()
            else:
                prods = Product.objects.filter(group_id=group_id)
            for p in prods:
                db_list[p.id] = []
                dbs = p.databases.all()
                for db in dbs:
                    db_list[p.id].append([db.id, db.database, p.id])
                prod_list.append([p.id, p.name])
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取项目、数据库信息列表失败：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (
            True, json.JSONEncoder().encode({'status': 'OK', 'msg': {'server_list': prod_list, 'db_list': db_list}}))

    @staticmethod
    def get_dbs(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        try:
            schema_version = []
            did = int(request.GET.get('did'))
            db = Dep_Sql.objects.get(id=did)
            url = db.db_host + ':' + db.db_port + ':' + db.db_name + ':' + db.db_user + ':' + db.db_pass
            schema_version.append(url + '<br />')
            jdbc = 'jdbc:mysql://' + db.db_host + ':' + db.db_port + '/' + db.db_name
            shell = ['sudo', conf.FLYWAYPATH + 'flyway', 'info', '-url=' + jdbc, '-user=' + db.db_user,
                     '-password=' + db.db_pass]
            output, err = Popen(shell, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
            if len(err) > 0:
                schema_version.append(err.decode('utf-8'))
            else:
                info = output.decode('utf-8').split('\n\n')[2].split('\n')
                for io in info:
                    schema_version.append(io + '<br />')
        except Exception as e:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': str(e)}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': schema_version}))

    @staticmethod
    def create_db(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
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
        Config.load_config_type('dbc_cmd')
        Config.load_config_type('ui_dbc')
        cmds = Config()['dbc_cmd']
        cmd_index = list(cmds.keys())
        cmd_index.sort()
        dbc = Config()['ui_dbc']
        db_user = dbc['db_user']['value']
        db_pass = dbc['db_user']['configuration']
        r = request.POST.get('request')
        j = json.loads(r)
        dbs = j['dbs']
        db_name = j['db_name']
        sqls = []
        for index in cmd_index:
            cmd = cmds[index]['value'].replace("${db_name}", db_name)
            cmd = cmd.replace("${db_user}", db_user)
            cmd = cmd.replace("${db_pass}", db_pass)
            sqls.append(cmd)
        databases = DBC.objects.filter(id__in=dbs)
        success_db = ""
        for db in databases:
            db_info = {
            'db_type': db.type,
            'db_host': db.db_host,
            'db_port': db.db_port,
            'db_user': db.db_user,
            'db_pass': db.db_pass,
            'db_name': None,
            'ssh_port': db.ssh_port,
            'ssh_user': db.ssh_user,
            'ssh_pass': db.ssh_pass,
            'ssh_key': db.ssh_key,
            }
            for sql in sqls:
                try:
                    result = SQL.run_sql_cmd(db_info, sql)
                except SQLError as e:
                    LOG('execdb', uid=uid).error(e.get_msg())
                    return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '数据库创建失败：' + e.get_msg()}))
                except Exception as e:
                    return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '数据库创建失败：' + e.args[0]}))
                if not result:
                    return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '数据库创建失败：run_sql_cmd'}))
                elif result is None:
                    return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '数据库创建失败：不支持所选数据库类型'}))
                else:
                    if len(result) > 3:
                        print('Create DB SQL other result:')
                        print(result)
            success_db += '[' + db.db_host + '] '
            LOG('execdb', uid=uid).info('数据库' + db_name + '@' + db.db_host + '创建成功')
        return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '数据库 ' + db_name + '@' + success_db + '创建成功'}))
