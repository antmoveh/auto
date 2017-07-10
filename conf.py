file_operators = ['cp', 'mv']

db_version_init = [
    'CREATE TABLE IF NOT EXISTS `db_version` (`id` INT(11) NOT NULL AUTO_INCREMENT,  `version` VARCHAR(21) NOT NULL, `version_p` INT(11) NOT NULL, `version_s` INT(11) NOT NULL, \
		`user` VARCHAR(20) NOT NULL, `time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, `status` VARCHAR(100) NULL DEFAULT \'\', PRIMARY KEY (`id`))  ENGINE=InnoDB;',
    'INSERT INTO `db_version` (`version`, `version_p`, `version_s`, `user`, `status`) VALUES (\'0.0\', 0, 0, \'auto\', \'init\');',
]

settings_file_location = '/data/applications/workspace/settings/'
settings_autotestfile_location = '/data/autotest/'

settings_file_name = {
    'data': 'data.cfg',
}

web_pages = {
    'index': 'INDEX_PAGE',
    'build': 'BUILD_PAGE',
    'deploy': 'DEPLOY_PAGE',
    'configuration': 'CONFIG_PAGE',
    'manage': 'MANAGE_PAGE',
    'about': 'ABOUT_PAGE',
}

basic_response = {
    'eds': ['服务器改动成功', '服务器改动失败', ],
    'set': ['配置文件设置成功', '配置文件设置失败', ],
    'ncf': ['配置文件添加成功', '配置文件添加失败', ],
    'gpl': ['', '', ],
    'dep': ['', '', ],
    'upd': ['', '', ],
}

USER_ADMIN = 1
USER_ANONYMOUS = 2
USER_ANONYMOUS_NAME = 'anonymous'
USER_DEFAULT = 3
USER_DEFAULT_NAME = 'auto'

PAGE_STEP = 20

FLYWAYPATH = '/data/applications/flyway-4.0.3/'
VFLYWAYPATH = '/data/applications/flyway-validate/'
local_dir = '/data/software/'
remote_dir = '/data/applications/'