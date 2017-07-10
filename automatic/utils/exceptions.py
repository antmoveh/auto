

class DeployError(Exception):
    msgs = {
        '001': '未指定部署目标主机',
        '002': '未定义部署程序步骤',
        '003': '未选定部署服务器',
        '004': '命令已执行，但有错误发生。',
        '005': 'File transfer error: Remote file path is not provided.',
        '006': 'File transfer error: Local file path is not provided.',
        '007': 'File transfer error: Local file md5 error.',
        '008': 'File transfer error: Remote file md5 error.',
        '009': '文件传输失败：MD5校验未通过',
        '010': 'Local file operate error: Operate command is not provided.',
        '011': 'Local file operate error: COPY source file path is not provided.',
        '012': 'Local file operate error: COPY destination file path is not provided.',
        '013': 'Local file operate error: Operate command is not supported, now support: mv, cp.',
        '014': 'Local file operate error: Source path not exist.',
        '015': 'Local file operate error: Destination directory not exist.',
        '016': 'Local file operate error: Operate command execute failed.',
        '017': 'Delete file error: Error occurred while deleting files.',
        '018': 'Tar error: Tar action is not provided.',
        '019': 'Tar error: Tar file name is not provided.',
        '020': 'Tar error: Create new tar ball path failed.',
        '021': 'Tar error: Archive creation failed.',
        '022': 'Tar error: Extract archive failed.',
        '023': 'Temp folder creation failed.',
        '024': 'Jar error: Action is not provided.',
        '025': 'Jar error: Jar/War file name is not provided.',
        '026': 'Jar error: Cannot find jar.',
        '027': 'Jar error: Jar/War operate failed.',
        '028': 'Database operation error: Database name is not provided.',
        '029': 'Database operation error: Import SQL with empty SQL file list.',
        '030': 'Database operation error: Cannot find database with provided name.',
        '031': '无法找到需要部署的文件',
        '032': 'Tomcat路径未定义',
        '033': '无法找到通用配置文件',
        '034': '未指定需要部署的子模块',
        '035': '未提供SQL文件所在路径',
        '036': '无法找到待部署版本信息',
        '037': 'SQL文件列表为空',
        '038': '创建db_version表失败',
        '039': '数据库连接信息不全',
        '040': 'SQL命令执行遇到错误',
        '041': '无法找到指定产品信息',
        '042': '无法找到指定子模块',
        '043': '无法找到部署路径信息',
    }

    def __init__(self, msg, value=None):
        self.msg = msg
        self.value = value

    def get_msg(self):
        r = self.msg
        if self.msg in list(self.msgs.keys()):
            r = self.msgs[self.msg]
        if self.value is not None:
            r += '\t' + self.value
        return r


class SshError(Exception):
    def __init__(self, msg, value=None):
        self.msg = msg
        self.value = value


class SQLError(Exception):
    msgs = {
        '001': '数据库连接信息不全',
        '002': 'SQL命令执行遇到错误',
        '003': '执行SQL脚本遇到错误',
        '004': '创建db_version表出错',
        '005': '获取数据库版本出错',
    }

    def __init__(self, msg, value=None):
        self.msg = msg
        self.value = value

    def get_msg(self):
        r = self.msg
        if self.msg in list(self.msgs.keys()):
            r = self.msgs[self.msg]
        if self.value is not None:
            r += '\t' + self.value
        return r
