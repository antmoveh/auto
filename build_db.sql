

INSERT INTO `auth` (`id`, `username`, `password`, `email`, `display`, `secret`, `active`) VALUES
	(1, 'admin', '1815a3ef3d4025798d30c88c3500da08', 'fushaosong@kokozu.net', '管理员', '2015-04-30 03:08:46', 'Y'),
	(2, 'fushaosong', '1815a3ef3d4025798d30c88c3500da08', 'fushaosong@kokozu.net', '付少松', '2015-04-30 03:08:46', 'Y');


INSERT INTO `configurations` (`id`, `type`, `name`, `value`, `configuration`, `param1`, `param2`, `active`) VALUES
	(1, 'env', 'log_file', '/data/log/auto.log', '', '', '', 'Y'),
	(2, 'env', 'log_db', 'log', '', '', '', 'Y'),
	(3, 'deploy', 'log_db', 'dep_log', '', '', '', 'Y'),
	(4, 'env', 'log_file_rotate', '10', '', '', '', 'Y'),
	(5, 'env', 'err_log', '/data/log/error.log', '', '', '', 'Y'),
	(6, 'env', 'log_file_size', '104857600', '', '', '', 'Y'),
	(7, 'env', 'log_file_lvl', 'DEBUG', '', '', '', 'Y'),
	(8, 'ui_nav', '1', '编译', 'build', '', '', 'Y'),
	(9, 'ui_nav', '2', '部署', 'deploy', '', '', 'Y'),
	(10, 'ui_nav', '3', '配置文件', 'configuration', '', '', 'Y'),
	(11, 'ui_nav', '7', '关于', 'about', '', '', 'Y'),
	(12, 'ui_nav', '5', '管理', 'manage', '', '', 'Y'),
	(15, 'ui_dbc', 'db_user', 'kdy_main', 'fh&*hfH924!9JfgJhnf', '', '', 'Y'),
	(16, 'dbc_cmd', '1', 'CREATE DATABASE ${db_name} DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;', '', '', '', 'Y'),
	(17, 'dbc_cmd', '2', 'grant all privileges on ${db_name}.* to \'${db_user}\'@\'localhost\' identified by \'${db_pass}\';', '', '', '', 'Y'),
	(18, 'dbc_cmd', '3', 'grant all privileges on ${db_name}.* to \'${db_user}\'@\'127.0.0.1\' identified by \'${db_pass}\';', '', '', '', 'Y'),
	(19, 'dbc_cmd', '4', 'grant all privileges on ${db_name}.* to \'${db_user}\'@\'106.2.186.%\' identified by \'${db_pass}\';', '', '', '', 'Y'),
	(20, 'dbc_cmd', '5', 'grant all privileges on ${db_name}.* to \'${db_user}\'@\'42.121.121.188\' identified by \'${db_pass}\';', '', '', '', 'Y'),
	(21, 'ui_nav', '6', '数据库', 'dbc', '', '', 'Y'),
	(22, 'ui_nav', '4', '项目环境', 'server', '', '', 'Y'),
	(23, 'configuration', 'storage', '/data/applications/workspace/git/configurations', '', '', '', 'Y'),
	(24, 'env', 'storage', '/data/nfs', '/data/nfs', '', '', 'Y'),
	(25, 'execdb', 'log_db', 'execdb_log', '', '', '', 'Y'),
	(26, 'env', 'temp', '/data/applications/temp', '', '', '', 'Y'),
	(28, 'env', 'bsp_url', '121.41.87.183:8000', '', '', '', 'Y'),
	(31, 'env', 'action_log', 'user_action', '', '', '', 'Y'),
	(36, 'ui_nav', '8', '用户', 'user', '', '', 'Y'),
	(37, 'dbc_cmd', '6', 'grant all privileges on ${db_name}.* to \'${db_user}\'@\'115.29.193.101\' identified by \'${db_pass}\';', '', '', '', 'Y'),
	(38, 'dbc_cmd', '7', 'grant all privileges on ${db_name}.* to \'${db_user}\'@\'10.%.%.%\' identified by \'${db_pass}\';', '', '', '', 'Y');


INSERT INTO `prod_jenkins` (`id`, `name`, `host`, `url`, `username`, `password`, `ssh_port`, `ssh_user`, `ssh_pass`, `ssh_key`, `storage`, `active`) VALUES
	(1, 'default', '192.168.227.128', 'http://192.168.227.128:1080/', 'bruce', 'ekWA62uG', '34846', 'kdy_yanfa', 'ssh_pass', '/data/applications/auto/id_rsa', '/data/build', 'Y');


INSERT INTO `user_permission` (`id`, `name`, `type`, `action`, `description`, `value`, `active`) VALUES
	(1, '创建DB', 'DBC', 'dbc', 'EXECDB_PAGE: DB Creation', '', 'Y'),
	(2, '添加DB主机', 'DBC', 'ndb', 'EXECDB_PAGE: Add new database host in DB Creation page', '', 'Y'),
	(3, '删除DB主机', 'DBC', 'ddh', 'EXECDB_PAGE: Remove DB host', '', 'Y'),
	(4, '修改项目服务器', 'SERVER', 'eds', 'SERVER_PAGE: Edit Server', '', 'Y'),
	(5, '禁用项目服务器', 'SERVER', 'dis', 'SERVER_PAGE: Disable Server', '', 'Y'),
	(6, '删除项目服务器', 'SERVER', 'des', 'SERVER_PAGE: Delete Server', '', 'Y'),
	(7, '修改配置文件', 'CONFIG', 'set', 'CONFIG_PAGE: Edit configuration file', '', 'Y'),
	(8, '粘贴配置文件', 'CONFIG', 'sea', 'CONFIG_PAGE: Set config file template with textarea input', '', 'Y'),
	(9, '删除专属配置', 'CONFIG', 'rcf', 'CONFIG_PAGE: Remove config file from selected server', '', 'Y'),
	(10, '恢复专属配置', 'CONFIG', 'ref', 'CONFIG_PAGE: Reverse config file from selected server backup file', '', 'Y'),
	(11, '删除配置文件', 'CONFIG', 'rmc', 'CONFIG_PAGE: Delete config file', '', 'Y'),
	(12, '新建配置文件', 'CONFIG', 'ncf', 'CONFIG_PAGE: New config file', '', 'Y'),
	(13, '启/禁用配置', 'CONFIG', 'tgc', 'CONFIG_PAGE: Toggle config file to enable/disable', '', 'Y'),
	(14, '部署', 'DEPLOY', 'dep', 'DEPLOY_PAGE: Deploy', '', 'Y'),
	(15, '添加产品项目', 'MANAGE', 'aup', 'MANAGE_PAGE: Add/Update product', '', 'Y'),
	(16, '启/禁用产品项目', 'MANAGE', 'dip', 'MANAGE_PAGE: Disable/Enable product', '', 'Y'),
	(17, '添加子模块', 'MANAGE', 'adm', 'MANAGE_PAGE: Add module to product', '', 'Y'),
	(18, '设置子模块', 'MANAGE', 'edm', 'MANAGE_PAGE: Edit module', '', 'Y'),
	(19, '启/禁用子模块', 'MANAGE', 'dim', 'MANAGE_PAGE: Disable/Enable module', '', 'Y'),
	(20, '删除子模块', 'MANAGE', 'rmm', 'MANAGE_PAGE: Remove module', '', 'Y'),
	(21, '配置子模块编译', 'MANAGE', 'amb', 'MANAGE_PAGE: Add/Edit module\'s build job', '', 'Y'),
	(22, '启/禁用部署命令', 'DEPLOY', 'dia', 'MANAGE_PAGE: Disable/Enable deploy action', '', 'Y'),
	(23, '修改部署命令', 'DEPLOY', 'eda', 'MANAGE_PAGE: Add/Edit deploy action', '', 'Y'),
	(24, '编译', 'BUILD', 'mkb', 'BUILD: Make build', '', 'Y'),
	(25, '添加分支', 'BUILD', 'adb', 'BUILD: Add branch', '', 'Y'),
	(26, '查看配置文加内容', 'CONFIG', 'ldc', 'CONFIG_PAGE: Get prod and module list in Configuration page', '', 'Y'),
	(27, '查看项目服务器', 'SERVER', 'sld', '#SERVER_PAGE: Load page', '', 'Y'),
	(28, '查看产品配置', 'MANAGE', 'ldm', 'MANAGE_PAGE: Load page data', '', 'Y'),
	(29, '查看DB主机', 'DBC', 'gsd', 'EXECDB_PAGE: Get server list and DB list', '', 'Y'),
	(30, '启/禁用测试工程', 'TEST', 'dit', 'MANAGE_PAGE: Disable/Enable test job', '', 'Y'),
	(31, '删除测试工程', 'TEST', 'rmt', 'MANAGE_PAGE: Delete test job', '', 'Y'),
	(32, '获取测试工程详情', 'TEST', 'gtd', 'MANAGE_PAGE: Get test job detail', '', 'Y'),
	(33, '添加/修改测试工程详情', 'TEST', 'edt', 'MANAGE_PAGE: Add/Edit test job', '', 'Y'),
	(34, '手动触发测试工程', 'TEST', 'tst', 'DEPLOY_PAGE: Manually trigger test', '', 'Y'),
	(35, '手动认证版本质量', 'BUILD', 'ctb', 'BUILD_PAGE: Certify build manually', '', 'Y');