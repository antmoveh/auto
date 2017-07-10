import paramiko


class SSHHelper():
    __ssh = None
    __transport = None
    __hostname = None
    __port = 22
    __username = None
    __password = None
    __key_file = None
    __timeout = None

    # Create SSH connection object, work_mod 'cmd' create SSHClient, 'sftp' create Transport
    def __init__(self, hostname, port=22, username=None, password=None, key_file=None, timeout=5):
        self.__hostname = hostname
        self.__port = port
        self.__username = username
        self.__password = password
        self.__key_file = key_file
        self.__timeout = timeout

    def __del__(self):
        if self.__ssh is not None:
            self.__ssh.close()
        if self.__transport is not None:
            self.__transport.close()

    def __connect_ssh(self):
        if len(self.__hostname) > 0 and len(self.__username) > 0 and len(self.__password) > 0:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.__key_file is not None:
                ssh.connect(self.__hostname, port=self.__port, username=self.__username, key_filename=self.__key_file,
                            timeout=self.__timeout)
            else:
                ssh.connect(self.__hostname, port=self.__port, username=self.__username, password=self.__password,
                            timeout=self.__timeout)
            self.__ssh = ssh

    def __connect_sftp(self):
        if len(self.__hostname) > 0 and len(self.__username) > 0 and len(self.__password) > 0:
            transport = paramiko.Transport((self.__hostname, self.__port))
            if self.__key_file is not None:
                private_key = paramiko.RSAKey.from_private_key_file(self.__key_file)
                transport.connect(username=self.__username, pkey=private_key)
            else:
                transport.connect(username=self.__username, password=self.__password)
            self.__transport = transport

    # Run commands from given list
    def run_command(self, cmd):
        if len(cmd) > 0:
            # print('Run cmd: ' + cmd)
            if self.__ssh is None:
                self.__connect_ssh()
            ssh = self.__ssh
            stdin, stdout, stderr = ssh.exec_command(cmd)
            outputs = stdout.readlines()
            errs = stderr.readlines()
            return (outputs, errs)
        else:
            return ([], ['No command to run.'])

    def copy_file(self, remote, local, action='push'):
        if len(remote) > 0 and len(local) > 0:
            # print('Remote file: ' + remote)
            # print('Local file: ' + local)
            if self.__transport is None:
                self.__connect_sftp()
            sftp = paramiko.SFTPClient.from_transport(self.__transport)
            if action == 'push':
                sftp.put(local, remote)
            elif action == 'pull':
                sftp.get(remote, local)
