import datetime
import os
import re
import shutil
import threading
import time
import conf
import automatic.utils.email as EMAIL
import automatic.utils.sql as SQL
import automatic.utils.utils as UTILS

from subprocess import Popen, PIPE
from automatic.utils.SSH import SSHHelper
from automatic.utils.config import Config
from automatic.utils.exceptions import DeployError, SQLError
from automatic.utils.log import LOG
from automatic.utils.server import SERVER
from automatic.utils.settings import SETTINGS
from automatic.models import *


class DEPLOY():
    server = None
    pid = None
    prod = None
    vid = None
    version = None
    uid = None
    username = None
    dep_status_id = None
    temp = None

    def __init__(self, s_id=None, s_name=None):
        if s_id is None and s_name is None:
            return False
        s = SERVER(s_id=s_id, s_name=s_name)
        if s.is_ready():
            self.server = s
        else:
            LOG('deploy').error('Cannot create deploy instance for [' + str(s_id) + ': ' + s_name + '].')

    def set_prod(self, pid=None, prod=None, bid=None, branch=None, vid=None, version=None):
        self.pid = pid
        self.prod = prod
        self.bid = bid
        self.branch = branch
        self.vid = vid
        self.version = version

    def set_user(self, uid=None, username=None):
        self.uid = uid
        self.username = username

    def deploy(self, host_dict=None, command_dict=None):
        server = Dep_Server.objects.filter(id=self.server.id)
        if len(server) > 0:
            server = server[0]
        else:
            return False
        prev_deps = Dep_Status.objects.filter(server=server, on_server='Y')
        for dep in prev_deps:
            dep.on_server = 'N'
            dep.save()
        branch = Prod_Branch.objects.filter(id=self.bid)
        if len(branch) > 0:
            branch = branch[0]
        else:
            return False
        prod = Product.objects.filter(id=self.pid)
        if len(prod) > 0:
            prod = prod[0]
        else:
            return False
        ver = Prod_Version.objects.filter(id=self.vid)
        if len(ver) > 0:
            ver = ver[0]
        else:
            return False
        u = Auth.objects.filter(id=self.uid)
        if len(u) > 0:
            u = u[0]
        else:
            return False
        dep_status = Dep_Status(server=server, prod=prod, branch=branch, version=ver, dep_user=u,
                                dep_time=datetime.datetime.now(), description='', dep_status='D', on_server='Y')
        dep_status.save()
        self.dep_status_id = dep_status.id
        if host_dict is None:
            host_dict = self.server.server_host
        if command_dict is None:
            command_dict = self.server.server_action
        host_dict[0] = ''
        for host_id in list(host_dict.keys()):
            if host_id in list(command_dict.keys()):
                host_command_list = command_dict[host_id]
            else:
                if 0 not in list(command_dict.keys()):
                    host_command_list = []
                else:
                    host_command_list = command_dict[0]
            if host_id not in list(self.server.server_path.keys()):
                paths = []
            else:
                paths = self.server.server_path[host_id]
            result_dict = {}
            for command in host_command_list:
                if command['prod_id'] == 0 or command['prod_id'] == self.pid:
                    cmd = command['operation']
                    try:
                        if cmd == 'dep_start':
                            result_dict[command['sequence']] = self.deploy_start()
                        elif cmd == 'tomcat':
                            if command['param2'] in paths:
                                result_dict[command['sequence']] = self.Tomcat(host_id=host_id,
                                                                               action=command['param1'],
                                                                               work_folder=paths[command['param2']][
                                                                                   'des_path'],
                                                                               script=command['param3'], \
                                                                               pid_path=command['param4'],
                                                                               force=command['param5'])
                            else:
                                LOG('deploy').warning('主机 ' + str(host_id) + ' 未找到Tomcat工作路径 ' + command['param2'],
                                                      self.dep_status_id)
                        elif cmd == 'sftp':
                            result_dict[command['sequence']] = self.File_transfer(host_id=host_id,
                                                                                  action=command['param1'],
                                                                                  remote_file=command['param2'],
                                                                                  local_file=command['param3'])
                        elif cmd == 'operate_file':
                            result_dict[command['sequence']] = self.operate_file(action=command['param1'],
                                                                                 file_src=command['param2'],
                                                                                 file_des=command['param3'])
                        elif cmd == 'tar':
                            result_dict[command['sequence']] = self.tar_file(action=command['param1'],
                                                                             tar_path=command['param2'],
                                                                             work_folder=command['param3'])
                        elif cmd == 'jar':
                            result_dict[command['sequence']] = self.java_package(action=command['param1'],
                                                                                 pak_path=command['param2'],
                                                                                 work_folder=command['param3'],
                                                                                 Manifest=command['param4'])
                        elif cmd == 'db_update':
                            #							result_dict[command['sequence']] = self.incre_db_update(database = command['param1'], work_folder = command['param2'])
                            result_dict[command['sequence']] = self.db_flyway(module=command['param1'],
                                                                              mode=command['param2'])
                        elif cmd == 'conf':
                            if command['param2'] in paths:
                                result_dict[command['sequence']] = self.deploy_conf(host_id=host_id,
                                                                                    module=command['param1'],
                                                                                    path=paths[command['param2']][
                                                                                        'des_path'])
                            else:
                                LOG('deploy').warning('主机 ' + str(host_id) + ' 未找到配置文件工作路径 ' + command['param2'],
                                                      self.dep_status_id)
                        elif cmd == 'deploy':
                            if command['param2'] in paths:
                                result_dict[command['sequence']] = self.deploy_code(host_id=host_id,
                                                                                    module=command['param1'],
                                                                                    path=paths[command['param2']],
                                                                                    deploy_local=command['param3'])
                            else:
                                LOG('deploy').warning('主机 ' + str(host_id) + ' 未找到部署工作路径 ' + command['param2'],
                                                      self.dep_status_id)
                        elif cmd == 'tomcod':
                            result_dict[command['sequence']] = self.TomCod(host_id=host_id, module=command['param1'],
                                                                           port=command['param2'],
                                                                           src_war=command['param3'], action='push')
                        elif cmd == 'dep_finish':
                            test_result = self.dep_finish(test_url=command['param1'])
                            result_dict[command['sequence']] = test_result
                            if not test_result:
                                dep_status = Dep_Status.objects.get(id=self.dep_status_id)
                                dep_status.dep_status = 'F'
                                dep_status.save()
                                return False
                    except (DeployError, SQLError) as e:
                        if self.dep_status_id is not None:
                            LOG('deploy').error(e.get_msg(), self.dep_status_id)
                        dep_status = Dep_Status.objects.get(id=self.dep_status_id)
                        dep_status.dep_status = 'F'
                        dep_status.save()
                        return False
        dep_status = Dep_Status.objects.get(id=self.dep_status_id)
        dep_status.dep_status = 'Y'
        dep_status.save()
        return True

    def deploy_start(self):
        temp = Config.get_config('env', 'temp')['value']
        if temp[-1:] != '/':
            temp += '/'
        temp += 't' + str(self.dep_status_id) + '/'
        if self.temp is None:
            os.makedirs(temp)
            self.temp = temp
        LOG('deploy').info('开始部署', self.dep_status_id)
        return True

    def get_conf_list(self, module=None):
        if module is None:
            try:
                prod = Product.objects.get(id=self.pid)
            except Exception as e:
                raise DeployError('041')
                return False
            else:
                return prod.configs.filter(active='Y')
        else:
            try:
                m = Prod_Module.objects.get(id=module, active='Y')
            except Exception as e:
                return None
            return m.configs.filter(active='Y')

    def deploy_conf_local(self, host_id=None, module=None, des=None):
        storage = Config.get_config('configuration', 'storage')['value']
        if storage[-1:] != '/':
            storage += '/'
        try:
            m = Prod_Module.objects.get(id=module)
        except Exception as e:
            raise DeployError('042')
            return False
        conf_files = self.get_conf_list(module)
        if des[-1:] != '/':
            des += '/'
        if self.temp is not None and os.path.isdir(self.temp):
            set = SETTINGS(m.name, self.server, host_id)
            for conf in conf_files:
                conf_name = conf.filename
                prod = conf.prod.name
                common = storage + prod + '/' + m.name + '/' + conf_name + '__0'
                host = storage + prod + '/' + m.name + '/' + conf_name + '__' + str(self.server.id)
                combined = self.temp + conf_name
                if not os.path.isfile(common):
                    raise DeployError('033')
                    return False
                des_path = conf.path
                if des_path[0] != '/':
                    des_path = des + des_path
                if des_path[-1] != '/':
                    des_path += '/'
                if not os.path.isfile(host):
                    LOG('deploy').warning('未找到主机专属配置文件，使用通用配置', self.dep_status_id)
                    shutil.copy(common, des_path + conf_name)
                else:
                    if set.get_combined_file(common=common, host=host, combined=combined):
                        shutil.copy(combined, des_path)
            return True
        else:
            return False

    def repackage_war(self, host_id=None, module=None, path=None):
        storage = Config.get_config('env', 'storage')['value']
        if storage[-1:] != '/':
            storage += '/'
        path_list = self.server.server_path[int(host_id)]
        try:
            m = Prod_Module.objects.get(id=int(module))
        except Exception as e:
            raise DeployError('042')
            return False
        dep_src_path = storage + self.prod + '/' + self.prod + '-' + self.branch + '/' + self.prod + '-' + self.version + '/' + m.name + '/'
        dep_src = dep_src_path + path['src_name']
        des_src_folder = path['src_name'][:path['src_name'].rfind('.war')]
        pak_path = self.java_package('extract', pak_path=dep_src, work_folder=self.temp + des_src_folder)
        if pak_path:
            self.deploy_conf_local(host_id, module, self.temp + des_src_folder)
        if not os.path.isdir(self.temp + 'war_files/'):
            os.makedirs(self.temp + 'war_files/')
        pak_path = self.java_package('create', pak_path=self.temp + 'war_files/' + path['src_name'],
                                     work_folder=self.temp + des_src_folder)
        UTILS.close_db()
        return pak_path

    def new_deploy_conf_local(self, confs=None, module=None, des=None):
        storage = Config.get_config('configuration', 'storage')['value']
        if storage[-1:] != '/':
            storage += '/'
        try:
            m = Prod_Module.objects.get(id=module)
        except Exception as e:
            raise DeployError('042')
            return False
        if des[-1:] != '/':
            des += '/'
        if self.temp is not None and os.path.isdir(self.temp):
            for con in confs:
                con_src = storage + m.prod.name + '/' + m.name + '/' + str(con.dpath_id) + '/' + con.pconf.filename
                des_path = des + con.path
                if des_path[-1] != '/':
                    des_path += '/'
                if os.path.isfile(con_src):
                    shutil.copy(con_src, des_path)
            return True
        else:
            return False

    def new_repackage_war(self, host_id=None, module=None, path=None, src_war=None):
        storage = Config.get_config('env', 'storage')['value']
        if storage[-1:] != '/':
            storage += '/'
        try:
            m = Prod_Module.objects.get(id=int(module))
            p = Dep_Path.objects.get(host_id=host_id, module=path)
            confs = p.dpaths.all()
        except Exception as e:
            raise DeployError('042')
            return False
        if confs.__len__() == 0:
            dep_src = storage + self.prod + '/' + self.prod + '-' + self.branch + '/' + self.prod + '-' + self.version + '/' + m.name + '/' + src_war
            return dep_src
        dep_src = storage + self.prod + '/' + self.prod + '-' + self.branch + '/' + self.prod + '-' + self.version + '/' + m.name + '/' + src_war
        des_src_folder = src_war[:src_war.rfind('.war')]
        pak_path = self.java_package('extract', pak_path=dep_src, work_folder=self.temp + des_src_folder)
        if pak_path:
            self.new_deploy_conf_local(confs, module, self.temp + des_src_folder)
        if not os.path.isdir(self.temp + 'war_files/'):
            os.makedirs(self.temp + 'war_files/')
        pak_path = self.java_package('create', pak_path=self.temp + 'war_files/' + src_war,
                                     work_folder=self.temp + des_src_folder)
        UTILS.close_db()
        return pak_path

    def deploy_conf(self, host_id=None, module=None, path=None):
        if host_id is None:
            raise DeployError('001')
            return False
        if module is None:
            raise DeployError('034')
            return False
        if path is None:
            raise DeployError('034')
            return False
        try:
            m = Prod_Module.objects.get(id=module)
        except Exception as e:
            raise DeployError('042')
            return False
        if self.pid is None or self.prod is None or self.vid is None or self.version is None:
            raise DeployError('036')
            return False
        conf_files = self.get_conf_list(module)
        if conf_files is None:
            LOG('deploy').warning('未找到 ' + m.name + ' 对应配置文件', self.dep_status_id)
            return False
        storage = Config.get_config('configuration', 'storage')['value']
        if storage[-1:] != '/':
            storage += '/'
        if self.temp is not None and os.path.isdir(self.temp):
            set = SETTINGS(m.name, self.server, host_id)
            for conf in conf_files:
                conf_name = conf.filename
                prod = conf.prod.name
                common = storage + prod + '/' + m.name + '/' + conf_name + '__0'
                host = storage + prod + '/' + m.name + '/' + conf_name + '__' + str(self.server.id)
                combined = self.temp + conf_name
                if set.get_combined_file(common=common, host=host, combined=combined):
                    if int(host_id) in list(self.server.server_path.keys()):
                        path_list = self.server.server_path[int(host_id)]
                    else:
                        raise DeployError('001')
                        return False
                    des_file = path
                    if des_file[-1:] != '/':
                        des_file += '/'
                    des_file += conf_name
                    try:
                        self.File_transfer(host_id, 'push', des_file, combined)
                    except DeployError as e:
                        if self.dep_status_id is not None:
                            LOG('deploy').error(e.get_msg(), self.dep_status_id)
                            return False
        else:
            return False
        return True

    def deploy_code(self, host_id=None, module=None, path=None, deploy_local=None):
        if host_id is None:
            raise DeployError('001')
            return False
        if module is None:
            raise DeployError('034')
            return False
        if path is None:
            raise DeployError('034')
            return False
        if self.pid is None or self.prod is None or self.vid is None or self.version is None:
            raise DeployError('036')
            return False
        storage = Config.get_config(type='env', name='storage')['value']
        if storage[-1:] != '/':
            storage += '/'
        if int(host_id) in list(self.server.server_host.keys()):
            host = self.server.server_host[int(host_id)]
        else:
            raise DeployError('001')
            return False
        try:
            m = Prod_Module.objects.get(id=int(module))
        except Exception as e:
            raise DeployError('042')
            return False
        if self.dep_status_id is not None:
            LOG('deploy').info('部署代码' + path['des_name'], self.dep_status_id)
        dep_src_path = storage + self.prod + '/' + self.prod + '-' + self.branch + '/' + self.prod + '-' + self.version + '/' + m.name + '/'
        dep_src = dep_src_path + path['src_name']
        if os.path.isfile(dep_src):
            if deploy_local == 'Y':
                src = self.repackage_war(host_id, module, path)
            else:
                src = dep_src
            ssh = SSHHelper(hostname=host['host'], port=int(host['port']), username=host['user'], password=host['pass'],
                            key_file=host['pkey'])
            dep_des = path['des_path']
            if dep_des[-1:] != '/':
                dep_des += '/'
            stage_folder = dep_des + 'staging/'
            stage_file = stage_folder + path['des_name']
            dep_des += 'webapps/' + path['des_name']
            if path['work_mod'] == 'WAR':
                rm_path = dep_des[:-4]
                cmd = 'if [ ! -d \"' + stage_folder + '\" ]; then sudo mkdir -p ' + stage_folder + '; fi; sudo chown ' + \
                      host['user'] + ':' + host['user'] + ' ' + stage_folder + ';'
                ssh.run_command(cmd)
                try:
                    self.File_transfer(host_id, 'push', stage_file, src)
                except (DeployError, SQLError) as e:
                    if self.dep_status_id is not None:
                        LOG('deploy').error(e.get_msg(), self.dep_status_id)
                    return False
                else:
                    ssh.run_command(
                        'sudo rm -r ' + rm_path + '; sudo rm ' + dep_des + '; sudo mv ' + stage_file + ' ' + dep_des + ';')
            elif path['work_mod'] == 'PHP':
                pass
        else:
            #raise DeployError('031')
            print(dep_src + ' not found.')
        #return True
        return True

    def Tomcat(self, host_id=None, action=None, work_folder=None, script=None, pid_path=None, force=None):
        if action == 'stop':
            a_mod = '关闭'
        else:
            a_mod = '启动'
        if self.dep_status_id is not None:
            LOG('deploy').info('开始 ' + a_mod + ' Tomcat', self.dep_status_id)
        if host_id is None:
            raise DeployError('001')
            return False
        if action is None:
            raise DeployError('002')
            return False
        if self.server is None:
            raise DeployError('003')
            return False
        host = self.server.server_host[host_id]
        if work_folder[-1:] != '/':
            work_folder += '/'
        ssh = SSHHelper(hostname=host['host'], port=int(host['port']), username=host['user'], password=host['pass'],
                        key_file=host['pkey'])
        pid_script = ''
        act_msg = None
        if action == 'start':
            shell_script = pid_script + 'cd ' + work_folder + '; sudo -E ' + script
            act_msg = '启动tomcat'
        if action == 'stop':
            if force is not None and force != '0':
                shell_script = 'sudo kill -9 `ps -ef | grep ' + work_folder + ' | grep -v grep | awk \'{print $2}\'`'
            else:
                shell_script = pid_script + 'cd ' + work_folder + '; sudo -E ' + script
            act_msg = '关闭tomcat'
        #print(shell_script)
        outputs, errs = ssh.run_command(shell_script)
        if len(errs) == 0:
            if self.dep_status_id is not None and act_msg is not None:
                LOG('deploy').info(act_msg + ': ' + str(outputs), self.dep_status_id)
            return True
        else:
            errs_output = str(errs)
            if re.search('sudo: unable to resolve host', errs_output) is not None:
                #if re.search('sudo: unable to resolve host', errs_output) is not None:
                if self.dep_status_id is not None and act_msg is not None:
                    LOG('deploy').warning('命令执行有错误发生: ' + errs_output, self.dep_status_id)
                    LOG('deploy').info(act_msg + ': ' + str(outputs), self.dep_status_id)
                return True
            if action == 'stop':
                if self.dep_status_id is not None and act_msg is not None:
                    LOG('deploy').info(act_msg + ': ' + str(errs), self.dep_status_id)
                return True
            raise DeployError('004', str(errs))
            return False

    def TomCod(self, host_id=None, module=None, port='9999', src_war='', action='push'):
        if host_id is None:
            raise DeployError('001')
            return False
        if module is None:
            raise DeployError('034')
            return False
        if port is None:
            raise DeployError('034')
            return False
        if self.pid is None or self.prod is None or self.vid is None or self.version is None:
            raise DeployError('036')
            return False
        storage = Config.get_config(type='env', name='storage')['value']
        if storage[-1:] != '/':
            storage += '/'
        if int(host_id) in list(self.server.server_host.keys()):
            host = self.server.server_host[int(host_id)]
        else:
            raise DeployError('001')
            return False
        try:
            m = Prod_Module.objects.get(id=int(module))
        except Exception as e:
            raise DeployError('042')
            return False
        ssh = SSHHelper(hostname=host['host'], port=int(host['port']), username=host['user'], password=host['pass'],
                        key_file=host['pkey'])
        #检查远程服务器上tomcat安装包
        try:
            local_md5 = self.__local_md5(conf.local_dir + 'tomcat.tar.gz')
            remote_md5 = self.__remote_md5(host_id, conf.remote_dir + 'source/tomcat.tar.gz')
            if local_md5 != remote_md5:
                shell = 'if [ ! -d \"' + conf.remote_dir + 'source' + '\" ]; then sudo mkdir -p ' + conf.remote_dir + 'source' + '; fi; sudo chown ' + \
                        host['user'] + ':' + host['user'] + ' ' + conf.remote_dir + 'source' + ';'
                ssh.run_command(shell)
                scp = self.File_transfer(host_id, 'push', conf.remote_dir + 'source/tomcat.tar.gz',
                                         conf.local_dir + 'tomcat.tar.gz')
                if scp:
                    cmd = 'if [ ! -d \"' + conf.remote_dir + 'source/tomcat.tar.gz' + '\" ]; then cd ' + conf.remote_dir + 'source; tar zxf tomcat.tar.gz; fi'
                    outputs, errs = ssh.run_command(cmd)
                    if len(errs) == 0:
                        LOG('deploy').info('校验Tomcat|完成' + str(host['host']), self.dep_status_id)
                    else:
                        print(errs)
                        LOG('deploy').info('校验Tomcat|失败' + str(host['host']), self.dep_status_id)
            else:
                LOG('deploy').info('校验Tomcat|完成' + str(host['host']), self.dep_status_id)
        except Exception as e:
            print(e)
            LOG('deploy').error('校验Tomcat失败，请检查|' + str(host['host']), self.dep_status_id)
            return False
        #创建指定端口号的tomcat
        try:
            tname = '/data/applications/tomcat' + str(port)
            tsource = '/data/applications/source'
            create = 'if [ -d \"' + tname + '\" ]; then sudo kill -9 `ps -ef | grep ' + tname + ' | grep -v grep | awk \'{print $2}\'`;' + \
                     'sudo mv ' + tname + '/webapps ' + tsource + ' && sudo mv ' + tname + '/logs ' + tsource + ' && sudo rm -rf ' + tname + '; fi;' + \
                     'sudo cp -rf /data/applications/source/tomcat ' + tname + ';' + \
                     'if [ -d "/data/applications/source/logs" ]; then sudo mv /data/applications/source/logs ' + tname + ' && sudo mv /data/applications/source/webapps ' + tname + '; fi;' + \
                     'sudo rm -rf ' + tname + '/webapps/' + src_war[0:-4] + '*; sudo chown -R ' + host['user'] + ':' + \
                     host['user'] + ' ' + tname + ' && ' + \
                     'sed -i \'s/8654/' + str(int(port) - 1357) + '/\' ' + tname + '/conf/server.xml;' + \
                     'sed -i \'s/8800/' + str(port) + '/\' ' + tname + '/conf/server.xml;' + \
                     'sed -i \'s/8429/' + str(int(port) - 2357) + '/\' ' + tname + '/conf/server.xml'
            outputs, errs = ssh.run_command(create)
            if len(errs) == 0:
                LOG('deploy').info('创建Tomcat|成功' + str(host['host']) + '|tomcat' + str(port), self.dep_status_id)
            else:
                LOG('deploy').error('创建Tomcat|失败' + str(host['host']) + '|tomcat' + str(port) + str(errs),
                                    self.dep_status_id)
            temp = 'ps -ef | grep ' + tname + ' | grep -v grep | awk \'{print $2}\''
            outputs, errs = ssh.run_command(temp)
            LOG('deploy').info('检查进程' + str(host['host']) + '|tomcat' + str(port) + '|' + str(outputs) + str(errs),
                               self.dep_status_id)
        except Exception as e:
            LOG('deploy').error('创建Tomcat|发生异常' + str(host['host']) + '|tomcat' + str(port) + str(e),
                                self.dep_status_id)
            return False
        #部署代码启动tomcat
        try:
            if self.dep_status_id is not None:
                LOG('deploy').info('部署代码|' + str(host['host']) + '|tomcat' + str(port), self.dep_status_id)
            dep_src = self.new_repackage_war(host_id, module, port, src_war)
            if os.path.isfile(dep_src):
                scp = self.File_transfer(host_id, 'push',
                                         conf.remote_dir + 'tomcat' + str(port) + '/webapps/' + src_war, dep_src)
                if scp:
                    LOG('deploy').info('部署代码|传输完成' + str(host['host']) + '|tomcat' + str(port), self.dep_status_id)
                    start = 'cd ' + conf.remote_dir + 'tomcat' + str(port) + '/bin; sudo ./startup.sh'
                    outputs, errs = ssh.run_command(start)
                    if len(errs) == 0:
                        LOG('deploy').info('启动Tomcat|成功' + str(host['host']) + '|tomcat' + str(port),
                                           self.dep_status_id)
                    else:
                        LOG('deploy').error('启动Tomcat|失败' + str(host['host']) + '|tomcat' + str(port),
                                            self.dep_status_id)
                else:
                    LOG('deploy').error('部署代码|传输失败', self.dep_status_id)
            else:
                LOG('deploy').error('部署代码|失败,请检查部署包是否存在', self.dep_status_id)
        except Exception as e:
            LOG('deploy').error('部署代码|失败' + str(host['host']) + '|tomcat' + str(port) + str(e), self.dep_status_id)
            return False

    def __sftp(self, host_id, action, remote_file, local_file):
        host = self.server.server_host[host_id]
        if host['pkey'] is None or host['pkey'] == '':
            ssh = SSHHelper(host['host'], port=int(host['port']), username=host['user'], password=host['pass'])
        else:
            ssh = SSHHelper(host['host'], port=int(host['port']), username=host['user'], password=host['pass'],
                            key_file=host['pkey'])
        ssh.copy_file(remote_file, local_file, action)

    def __local_md5(self, file):
        output, err = Popen(['md5sum', file], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
        if len(err) > 0:
            raise DeployError('007')
            return None
        else:
            return output.decode('utf-8')[:32]

    def __remote_md5(self, host_id, remote_file):
        host = self.server.server_host[host_id]
        if host['pkey'] is None or host['pkey'] == '':
            ssh = SSHHelper(host['host'], port=int(host['port']), username=host['user'], password=host['pass'])
        else:
            ssh = SSHHelper(host['host'], port=int(host['port']), username=host['user'], password=host['pass'],
                            key_file=host['pkey'])
        outputs, errs = ssh.run_command('md5sum ' + remote_file)
        if len(errs) == 0:
            return outputs[0][:32]
        else:
            #			raise DeployError('008', errs.decode('utf-8'))
            return 'null'


    def File_transfer(self, host_id=None, action=None, remote_file=None, local_file=None):
        if host_id is None:
            raise DeployError('001')
            return False
        if action is None:
            raise DeployError('002')
            return False
        if (remote_file is None ) or (len(remote_file) == 0):
            raise DeployError('005')
            return False
        if (local_file is None ) or (len(local_file) == 0):
            raise DeployError('006')
            return False

        local_md5 = ''
        remote_md5 = ''
        if action == 'push':
            local_md5 = self.__local_md5(local_file)
            self.__sftp(host_id, action, remote_file, local_file)
            remote_md5 = self.__remote_md5(host_id, remote_file)
        elif action == 'pull':
            remote_md5 = self.__remote_md5(host_id, remote_file)
            self.__sftp(host_id, action, remote_file, local_file)
            local_md5 = self.__local_md5(local_file)
        if local_md5 == remote_md5:
            return True
        else:
            raise DeployError('009', 'Local MD5: ' + local_md5 + '\tRemote MD5: ' + remote_md5)
            return False

    def operate_file(self, action=None, file_src=None, file_des=None):
        if action is None:
            raise DeployError('010')
            return False
        if (file_src is None ) or (len(file_src) == 0):
            raise DeployError('011')
            return False
        if (file_des is None ) or (len(file_des) == 0):
            raise DeployError('012')
            return False
        if action not in conf.file_operators:
            raise DeployError('013')
            return False
        if not os.path.exists(file_src):
            raise DeployError('014')
            return False
        if not os.path.dirname(file_des):
            raise DeployError('015')
            return False
        param = '-f'
        if (action != 'mv') and (os.path.isdir(file_src)):
            param = '-rf'
        output, err = Popen([action, param, file_src, file_des], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
        if len(err) > 0:
            raise DeployError('016', err.decode('utf-8'))
            return False
        return True

    def rm_file(self, host_id=None, file=None):
        if host_id is None:
            ouput, err = Popen(['rm', '-rf', file], stdout=PIPE, stderr=PIPE).communicate()
            if len(err) > 0:
                raise DeployError('017', err.decode('utf-8'))
                return False
        else:
            host = self.server.server_host[host_id]
            if host['pkey'] == '':
                ssh = SSHHelper(host['host'], port=int(host['port']), username=host['user'], password=host['pass'])
            outputs, errs = ssh.run_command('rm -rf ' + file)
            if len(errs) > 0:
                raise DeployError('017', str(errs))
                return False
        return True

    def tar_file(self, action=None, tar_path=None, work_folder=None):
        if action is None:
            raise DeployError('018')
            return False
        if tar_path is None:
            raise DeployError('019')
            return False
        if (work_folder is None ) or (len(work_folder) == 0):
            work_folder = UTILS.get_temp_folder('tar')

        if action == 'create':
            create_path = os.path.dirname(tar_path)
            act_script = ['czf', tar_path]
            if os.path.isfile(work_folder):
                work_script = ['-C', os.path.dirname(work_folder), os.path.basename(work_folder)]
            else:
                work_script = ['-C', work_folder, '.']
            err_code = '021'
            r_value = tar_path
        elif action == 'extract':
            create_path = os.path.dirname(work_folder)
            act_script = ['xzf', tar_path]
            work_script = ['-C', work_folder]
            err_code = '022'
            r_value = work_folder
        else:
            return False
        tar_script = ['tar'] + act_script + work_script
        if UTILS.mkdir(create_path, '020'):
            output, err = Popen(['tar'] + act_script + work_script, stdout=PIPE, stderr=PIPE).communicate()
            if len(err) > 0:
                raise DeployError(err_code, err.decode('utf-8'))
                return False
            else:
                return r_value
        else:
            return False

    def java_package(self, action=None, pak_path=None, work_folder=None, Manifest=None):
        if action is None:
            raise DeployError('024')
            return False
        if pak_path is None:
            raise DeployError('025')
            return False
        if (work_folder is None ) or (len(work_folder) == 0):
            work_folder = UTILS.get_temp_folder('java')
        jar = None
        for java_path in UTILS.Java_path:
            if os.path.isfile(java_path + '/bin/jar'):
                jar = java_path + '/bin/jar'

        if jar is None:
            raise DeployError('026')
            return False

        if action == 'create':
            create_path = os.path.dirname(pak_path)
            if os.path.isfile(work_folder):
                work_script = ['-C', os.path.dirname(work_folder), os.path.basename(work_folder)]
            else:
                work_script = ['-C', work_folder, '.']
            if (Manifest is None ) or (len(Manifest) == 0):
                act_script = ['cf', pak_path]
            else:
                act_script = ['cmf', Manifest, pak_path]
            cwd = None
        elif action == 'extract':
            create_path = work_folder
            act_script = ['xf', pak_path]
            work_script = []
            cwd = work_folder
        else:
            return False

        jar_script = [jar] + act_script + work_script
        if UTILS.mkdir(create_path, '020'):
            output, err = Popen(jar_script, stdout=PIPE, stderr=PIPE, cwd=cwd).communicate()
            if len(err) > 0:
                raise DeployError('027', err.decode('utf-8'))
                return False
            else:
                return pak_path
        else:
            return False

    def dbu_log(self, db_info, sql):
        version = sql.split('_')[1]
        desc = sql.split('_')[2][:-4]
        version_v = version.split('.')
        script = 'INSERT INTO `db_version` (`version`, `version_p`, `version_s`, `user`, `status`) VALUES (\'' + version + '\', \'' + \
                 version_v[0] + '\', \
			\'' + version_v[1] + '\', \'auto\', \'' + desc + '\');'
        try:
            output = SQL.run_sql_cmd(db_info, script)
        except (DeployError, SQLError) as e:
            if self.dep_status_id is not None:
                LOG('deploy').error(e.get_msg(), self.dep_status_id)
            return False
        return True

    def db_flyway(self, module=None, mode=None):
        storage = Config.get_config(type='env', name='storage')['value']
        if storage[-1:] != '/':
            storage += '/'  #storage = /data/nfs/
        try:
            m = Prod_Module.objects.get(id=int(module))
        except Exception as e:
            raise DeployError('042')
            return False
        product = Product.objects.filter(id=self.pid)
        db = Dep_Sql.objects.get(prod=product)
        jdbc = 'jdbc:mysql://' + db.db_host + ':' + db.db_port + '/' + db.db_name
        db_path = 'filesystem:' + storage + self.prod + '/' + self.prod + '-' + self.branch + '/' + self.prod + '-' + self.version + '/' + m.name + '/db'
        shell = ['sudo', conf.FLYWAYPATH + 'flyway', 'migrate', '-url=' + jdbc, '-user=' + db.db_user,
                 '-password=' + db.db_pass, '-locations=' + db_path, '-baselineOnMigrate=true']
        output, err = Popen(shell, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
        validate = ['sudo', conf.VFLYWAYPATH + 'flyway', 'validate', '-url=' + jdbc, '-user=' + db.db_user,
                    '-password=' + db.db_pass, '-locations=' + db_path]
        t = threading.Thread(target=self.db_flyway_validate, args=(validate,))
        t.start()
        if len(err) > 0:
            LOG('deploy').error('执行SQL出错：' + str(err.decode('utf-8')), self.dep_status_id)
            shell = ['sudo', conf.FLYWAYPATH + 'flyway', 'repair', '-url=' + jdbc, '-user=' + db.db_user,
                     '-password=' + db.db_pass, '-locations=' + db_path]
            output2, err2 = Popen(shell, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
            if len(err2) > 0:
                LOG('deploy').error('执行恢复出错：' + str(err2.decode('utf-8')), self.dep_status_id)
            else:
                LOG('deploy').info('执行恢复成功：' + str(output2.decode('utf-8')), self.dep_status_id)
            return False
        else:
            LOG('deploy').info('执行SQL成功: ' + str(output.decode('utf-8')), self.dep_status_id)
            return True

    def db_flyway_validate(self, shell):
        times = [1, 3, 5, 10, 20, 30, 30, 30, 30, 60, 60, 60]
        for t in times:
            time.sleep(t * 60)
            output, err = Popen(shell, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
            if len(err) > 0:
                LOG('deploy').error('数据库升级失败：' + str(err.decode('utf-8')), self.dep_status_id)
                dep_status = Dep_Status.objects.get(id=self.dep_status_id)
                dep_status.dep_status = 'F'
                LOG('deploy').info('部署失败', self.dep_status_id)
                dep_status.save()
                break
            else:
                LOG('deploy').info('数据库升级完成：' + str(output.decode('utf-8')), self.dep_status_id)
                dep_status = Dep_Status.objects.get(id=self.dep_status_id)
                dep_status.dep_status = 'Y'
                dep_status.save()
                LOG('deploy').info('部署成功', self.dep_status_id)
                break


    def incre_db_update(self, database=None, work_folder=None):
        if database is None or len(database) == 0:
            raise DeployError('028')
            return False
        if work_folder is None or len(database) == 0:
            raise DeployError('029')
            return False
        if self.dep_status_id is not None:
            LOG('deploy').info('开始进行数据库增量升级', self.dep_status_id)
        if database in self.server.server_db:
            db_info = self.server.get_db_info(database)
        else:
            raise DeployError('030', database)
            return False
        sql_list = SQL.get_sql_files(work_folder)
        done_index = SQL.sql_done_index(SQL.get_db_version(db_info))
        sql_dict = {}
        sql_index = []
        for sql in sql_list:
            sql_db, sql_v, sql_desc = SQL.get_sqlfile_info(sql)
            s_index = int(sql_v.split('.')[0]) * 1000 + int(sql_v.split('.')[1])
            sql_dict[s_index] = sql
            sql_index.append(s_index)
        sql_index = SQL.rm_done_sql(sql_index=sql_index, done_index=done_index)
        sql_index.sort()
        sql_done = []
        for index in sql_index:
            try:
                output = SQL.run_sql_file(db_info, work_folder + sql_dict[index])
            except (DeployError, SQLError) as e:
                if self.dep_status_id is not None:
                    LOG('deploy').error(e.get_msg(), self.dep_status_id)
                return False
            if (output is not None ) and (output != False):
                if not self.dbu_log(db_info, sql_dict[index]):
                    return False
                sql_done.append(sql_dict[index])
        if self.dep_status_id is not None:
            LOG('deploy').info('数据库增量升级完成, 执行SQL: ' + str(sql_done), self.dep_status_id)
        return True

    def dep_finish(self, test_url):
        #if self.temp != None:
        #	if os.path.exists(self.temp):
        #		shutil.rmtree(self.temp)
        if test_url is None or len(test_url) < 1:
            if self.dep_status_id is not None:
                LOG('deploy').info('部署成功', self.dep_status_id)
            return True
        if self.dep_status_id is not None:
            LOG('deploy').info('测试服务', self.dep_status_id)
        if UTILS.check_service(test_url, self.dep_status_id):
            if self.dep_status_id is not None:
                LOG('deploy').info('部署成功', self.dep_status_id)
            return True
        else:
            if self.dep_status_id is not None:
                LOG('deploy').info('部署失败, 服务未启动', self.dep_status_id)
            return False

    def send_deploy_email(self):
        dep = Dep_Status.objects.get(id=self.dep_status_id)
        tz_diff = datetime.timedelta(hours=8)
        if dep.dep_status == 'Y':
            status = '成功'
        else:
            status = '失败'
        logs = []
        dep_logs = Dep_Log.objects.filter(iid=dep.id)
        for log in dep_logs:
            logs.append({'time': str(log.time + tz_diff), 'status': log.status, 'detail': log.detail})
        pid = dep.prod.id
        sid = dep.server.id
        subscribes = User_Subscribe.objects.filter(prod_id__in=[0, pid], server_id__in=[0, sid], deploy='Y')
        cc = []
        for s in subscribes:
            if s.deploy == 'Y':
                cc.append(s.user.email)
        cc = list(set(cc))
        if dep.dep_user.email in cc:
            cc.remove(dep.dep_user.email)
        dep_detail = {
            'status': status,
            'server': dep.server.server,
            'prod': dep.prod.name,
            'version': dep.version.version,
            'user': dep.dep_user.display,
            'time': str(dep.dep_time + tz_diff),
            'logs': logs,
        }
        subject = '服务器 ' + dep.server.server + ' 部署 ' + status
        EMAIL.mail(subject=subject, mode='deploy', html_context=dep_detail, to_mail=[dep.dep_user.email], cc=cc,
                   text_content=subject)

#
