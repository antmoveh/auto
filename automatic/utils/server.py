from .exceptions import DeployError
from .log import LOG
from automatic.models import *


class SERVER():
    def __init__(self, s_id=None, s_name=None):
        self.id = None
        self.server_name = None
        self.server_host = {}
        self.server_db = {}
        self.server_path = {}
        self.server_action = {}
        if s_id is None and s_name is None:
            return False
        log = LOG('svr_info', False)
        if s_id is None:
            try:
                server = Dep_Server.objects.filter(server=s_name)[0]
            except IndexError:
                log.error('Cannot find server with name: ' + s_name)
                return
            else:
                s_id = server.id
        else:
            try:
                server = Dep_Server.objects.filter(id=s_id)[0]
            except IndexError:
                log.error('Cannot find server with id: ' + str(s_id))
                return
            else:
                s_name = server.server
        self.id = server.id
        self.server_name = s_name
        try:
            host_list = server.hosts.all()
        except Exception as e:
            log.warning(e.args[0])
        else:
            if len(host_list) == 0:
                log.warning('Cannot find [' + s_name + ']\'s host data.')
            else:
                for host in host_list:
                    self.server_host[host.id] = {'host': host.host, 'port': host.ssh_port, 'user': host.ssh_user,
                                                 'pass': host.ssh_pass, 'pkey': host.ssh_file}
                    try:
                        path_list = host.paths.all()
                    except IndexError:
                        log.warning('Cannot find <' + host.host + '>@[' + s_name + ']\'s working path data.')
                    else:
                        if len(path_list) == 0:
                            log.warning('Cannot find <' + host.host + '>@[' + s_name + ']\'s working path data.')
                        else:
                            s_p = {}
                            for path in path_list:
                                s_p[path.module] = {'module': path.module, 'work_mod': path.work_mod,
                                                    'src_name': path.src_name, 'des_path': path.des_path,
                                                    'des_name': path.des_name}
                            self.server_path[host.id] = s_p
        try:
            db_list = server.databases.all()
        except IndexError:
            log.warning('Cannot find [' + s_name + ']\'s database connection data.')
        else:
            if len(db_list) == 0:
                log.warning('Cannot find [' + s_name + ']\'s database connection data.')
            else:
                for db in db_list:
                    self.server_db[db.database] = {'host': db.db_host, 'type': db.db_type, 'name': db.db_name,
                                                   'port': db.db_port, 'user': db.db_user, 'pass': db.db_pass}
        for action_host_id in ([0] + list(self.server_host.keys())):
            try:
                action_list = Dep_Action.objects.filter(server_id=self.id, host_id=action_host_id, active='Y')
            except IndexError:
                log.warning('Cannot find [' + s_name + ']\'s deploy action data.')
            else:
                if len(action_list) == 0:
                    if action_host_id == 0:
                        log.warning('Cannot find [' + s_name + ']\'s standard deploy action data.')
                else:
                    actions = []
                    action_list = action_list.order_by('sequence')
                    for action in action_list:
                        actions.append({'id': action.id, 'prod_id': action.prod_id, 'sequence': action.sequence,
                                        'operation': action.operation, 'param1': action.param1, 'param2': action.param2, \
                                        'param3': action.param3, 'param4': action.param4, 'param5': action.param5})
                    self.server_action[action_host_id] = actions
        log.info('Load server [' + s_name + ']\'s configurations.')

    def is_ready(self):
        if self.id is not None:
            return True
        else:
            return False

    def get_db_info(self, database=None):
        if database is None:
            raise DeployError('36')
        db_info = {}
        if database in self.server_db:
            db_info['db_host'] = self.server_db[database]['host']
            db_info['db_type'] = self.server_db[database]['type']
            db_info['db_name'] = self.server_db[database]['name']
            db_info['db_port'] = self.server_db[database]['port']
            db_info['db_user'] = self.server_db[database]['user']
            db_info['db_pass'] = self.server_db[database]['pass']
            return db_info
        else:
            return False
