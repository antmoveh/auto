import datetime
import logging
import logging.handlers
import conf
from .config import Config
from automatic.models import *


class LOG():
    log = None
    log_db = None
    module = None
    ilvl = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    log_dbs = {
        'deploy': Dep_Log,
        'execdb': Execdb_Log,
    }

    def get_handler(self, mod, log_file, maxBytes, backupCount, log_level):
        handler = None
        if mod == 'F':
            handler = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=maxBytes,
                                                           backupCount=backupCount)
        elif mod == 'S':
            handler = logging.StreamHandler()
        if handler is not None:
            handler.setLevel(LOG.ilvl[log_level])
            formatter = logging.Formatter('%(levelname)-8s %(name)-8s %(asctime)-24s: %(message)s')
            handler.setFormatter(formatter)
        return handler

    def __init__(self, module='default', console=True, uid=conf.USER_DEFAULT):
        self.module = module
        self.uid = uid
        log_file = None
        log_file_rotate = '10'
        log_file_size = '104857600'
        log_level = 'INFO'
        err_log = None
        Config.load_config_type('env')
        config = Config()
        env_config = Config()['env']
        if 'log_file' in env_config:
            log_file = env_config['log_file']['value']
        if 'log_file_rotate' in env_config:
            log_file_rotate = env_config['log_file_rotate']['value']
        if 'log_file_size' in env_config:
            log_file_size = env_config['log_file_size']['value']
        if 'log_file_lvl' in env_config:
            log_level = env_config['log_file_lvl']['value']
        if 'err_log' in env_config:
            err_log = env_config['err_log']['value']
        if 'log_db' in env_config:
            self.log_db = env_config['log_db']['value']

        if log_file is not None:
            self.log = logging.getLogger(module)
            if not self.log.handlers:
                self.log.setLevel(LOG.ilvl[log_level])
                h = self.get_handler('F', log_file, int(log_file_size), int(log_file_rotate), log_level)
                if h is not None:
                    self.log.addHandler(h)
                if err_log is not None:
                    h = self.get_handler('F', err_log, int(log_file_size), int(log_file_rotate), 'ERROR')
                    if h is not None:
                        self.log.addHandler(h)

                if module != 'default':
                    Config.load_config_type(module)
                    module_c = Config()[module]
                    module_log_file = None
                    module_log_level = 'INFO'
                    if 'log_file' in module_c:
                        module_log_file = module_c['log_file']['value']
                    if 'log_file_lvl' in module_c:
                        module_log_level = module_c['log_file_lvl']['value']
                    if module_log_file is not None:
                        h = self.get_handler('F', module_log_file, int(log_file_size), int(log_file_rotate),
                                             module_log_level)
                        if h is not None:
                            self.log.addHandler(h)
                if console:
                    h = self.get_handler('S', None, None, None, log_level)
                    if h is not None:
                        self.log.addHandler(h)

    def log_to_db(self, status, message, iid=-1):
        if self.module in list(self.log_dbs.keys()):
            user = self.uid
            if iid > 0:
                dep = Dep_Status.objects.filter(id=iid)
                if len(dep) > 0:
                    user = dep[0].dep_user.id
            db_log = self.log_dbs[self.module](iid=iid, user=user, time=datetime.datetime.now(), status=status,
                                               detail=message)
            db_log.save()

    def debug(self, message, iid=-1):
        self.log.debug(message)

    # self.log_to_db('DEBUG', message, iid)

    def action(self, action, message, type='action', uid=conf.USER_DEFAULT):
        extra_info = ''
        try:
            user = Auth.objects.get(id=uid)
        except Exception as e:
            print('无法获取指定用户：' + e.args[0])
            try:
                user = Auth.objects.get(id=1)
            except Exception as e:
                print('无法获取默认用户(uid = 1)：' + e.args[0])
                return False
            extra_info = '用户数据缺失，记录为默认用户(uid = 1)'
        t = datetime.datetime.now()
        action_log = User_Action(user=user, time=t, type=type, action=action, detail=message, extra_info=extra_info,
                                 status='A', result='', done_time=t)
        action_log.save()
        return action_log.id

    def done(self, id, status='D', result=''):
        if len(status) > 1:
            status = status[0]
        try:
            action_log = User_Action.objects.get(id=id)
        except Exception as e:
            print('更新用户行为日志失败：' + e.args[0])
            return False
        else:
            action_log.status = status
            action_log.result = result
            action_log.done_time = datetime.datetime.now()
            action_log.save()
            return True

    def info(self, message, iid=-1):
        self.log.info(message)
        self.log_to_db('INFO', message, iid)

    def warning(self, message, iid=-1):
        self.log.warning(message)
        self.log_to_db('WARNING', message, iid)

    def error(self, message, iid=-1):
        self.log.error(message)
        self.log_to_db('ERROR', message, iid)

    def critical(self, message, iid=-1):
        self.log.critical(message)
        self.log_to_db('CRITICAL', message, iid)
