import os, re
import conf
from subprocess import Popen, PIPE
from .exceptions import DeployError, SQLError
from .SSH import SSHHelper


def get_sqlfile_info(sql_file):
    if (sql_file is None ) or (len(sql_file) < 3):
        return False
    sql_info = sql_file.split('_')
    return (sql_info[0], sql_info[1], sql_info[2].split('.')[0])


def run_sql_cmd_local(db_info, cmd):
    db_type = db_info['db_type']
    db_host = db_info['db_host']
    db_port = db_info['db_port']
    db_user = db_info['db_user']
    db_pass = db_info['db_pass']
    db_name = db_info['db_name']
    if db_type == 'MYSQL':
        if db_name == '' or db_name is None:
            script = ['mysql', '-h' + db_host, '-P' + db_port, '-u' + db_user, '-p' + db_pass, '-e', cmd]
        else:
            script = ['mysql', '-h' + db_host, '-P' + db_port, '-u' + db_user, '-p' + db_pass, db_name, '-e', cmd]
        output, err = Popen(script, stdout=PIPE, stderr=PIPE).communicate()
        if len(err) > 0:
            raise SQLError('002', err.decode('utf-8'))
        else:
            return output.decode('utf-8')
    else:
        return None


def run_sql_cmd(db_info, cmd, local=False):
    if ('db_type' in db_info) and ('db_host' in db_info) and ('db_port' in db_info) and ('db_user' in db_info) and (
                'db_pass' in db_info) and ('db_name' in db_info):
        db_type = db_info['db_type']
        db_host = db_info['db_host']
        db_port = db_info['db_port']
        db_user = db_info['db_user']
        db_pass = db_info['db_pass']
        db_name = db_info['db_name']
    else:
        raise SQLError('001')
    if db_user != 'root':
        return run_sql_cmd_local(db_info, cmd)
    if db_host == 'localhost' or db_host == '127.0.0.1':
        return run_sql_cmd_local(db_info, cmd)
    else:
        if ('db_type' in db_info) and ('db_host' in db_info) and ('db_port' in db_info):
            ssh_host = db_host
            ssh_port = db_info['ssh_port']
            ssh_user = db_info['ssh_user']
            ssh_pass = db_info['ssh_pass']
            ssh_key = db_info['ssh_key']
            db_host = 'localhost'
            if db_name is None or db_name == '':
                db_name = ''
            else:
                db_name = ' ' + db_name
        else:
            raise SQLError('001')
        if db_type == 'MYSQL':
            cmd = 'mysql -h' + db_host + ' -P' + db_port + ' -u' + db_user + ' -p' + db_pass + db_name + ' -e \"' + cmd + '\"'
            if os.path.isfile(ssh_key):
                ssh = SSHHelper(hostname=ssh_host, port=int(ssh_port), username=ssh_user, password=ssh_pass,
                                key_file=ssh_key)
            else:
                ssh = SSHHelper(hostname=ssh_host, port=int(ssh_port), username=ssh_user, password=ssh_pass)
            output, errs = ssh.run_command(cmd)
            if len(errs) == 0:
                return output
            else:
                raise SQLError('002', str(errs))
        else:
            return None


def run_sql_file(db_info, sql_file):
    if ('db_type' in db_info) and ('db_host' in db_info) and ('db_port' in db_info) and ('db_user' in db_info) and (
                'db_pass' in db_info) and ('db_name' in db_info):
        db_type = db_info['db_type']
        db_host = db_info['db_host']
        db_port = db_info['db_port']
        db_user = db_info['db_user']
        db_pass = db_info['db_pass']
        db_name = db_info['db_name']
    else:
        raise SQLError('001')
    if db_type == 'MYSQL':
        script = 'mysql -h' + db_host + ' -P' + db_port + ' -u' + db_user + ' -p' + db_pass + ' ' + db_name + ' < ' + sql_file
        output, err = Popen(script, shell=True, stdout=PIPE, stderr=PIPE).communicate()
        if len(err) > 0:
            raise SQLError('003', err.decode('utf-8'))
        else:
            return output.decode('utf-8')
    else:
        return None


def create_db_version(db_info):
    if ('db_type' in db_info) and ('db_host' in db_info) and ('db_port' in db_info) and ('db_user' in db_info) and (
                'db_pass' in db_info) and ('db_name' in db_info):
        for sql in conf.db_version_init:
            try:
                run_sql_cmd(db_info, sql)
            except SQLError as e:
                raise SQLError('004', e.value)
        return True
    else:
        raise SQLError('001')


def get_db_version(db_info):
    if ('db_type' in db_info) and ('db_host' in db_info) and ('db_port' in db_info) and ('db_user' in db_info) and (
                'db_pass' in db_info) and ('db_name' in db_info):
        db_type = db_info['db_type']
        db_host = db_info['db_host']
        db_port = db_info['db_port']
        db_user = db_info['db_user']
        db_pass = db_info['db_pass']
        db_name = db_info['db_name']
    else:
        raise SQLError('001')
    if db_type == 'MYSQL':
        script = 'mysql -h' + db_host + ' -P' + db_port + ' -u' + db_user + ' -p' + db_pass + ' ' + db_name + ' -e \'SELECT version, version_p, version_s FROM db_version ORDER BY version_p, version_s;\''
        output, err = Popen(script, shell=True, stdout=PIPE, stderr=PIPE).communicate()
        if len(err) > 0:
            err_msg = err.decode('utf-8')
            c_r = False
            if (re.search('.db_version\' doesn\'t exist', err_msg) is not None ):
                try:
                    c_r = create_db_version(db_info)
                except SQLError as e:
                    print(e.msg, e.value)
            if c_r:
                output, err = Popen(script, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            if len(err) > 0 or c_r != True:
                raise SQLError('005', err.decode('utf-8'))
            else:
                return output.decode('utf_8').split('\n')[1:-1]
        else:
            return output.decode('utf_8').split('\n')[1:-1]
    else:
        return None


def sql_done_index(dbv_list=None):
    if dbv_list is None:
        return None
    done_index = []
    for dbv in dbv_list:
        v = dbv.split('\t')
        done_index.append(int(v[1]) * 1000 + int(v[2]))
    return done_index


def rm_done_sql(sql_index=None, done_index=None):
    if (sql_index is None ) or (done_index is None ):
        raise DeployError('037')
    for done_v in done_index:
        if sql_index.count(done_v) > 0:
            sql_index.remove(done_v)
    return sql_index


def get_sql_files(work_folder=None):
    if (work_folder is None ):
        raise DeployError('035')
    sql_list = []
    for roots, dirs, files in os.walk(work_folder):
        for file in files:
            if file.endswith('.sql'):
                sql_list.append(file)
    return sql_list
