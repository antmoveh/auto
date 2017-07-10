from django.db import models


class Auth(models.Model):
    class Meta:
        db_table = 'auth'

    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=32)
    email = models.CharField(max_length=100)
    display = models.CharField(max_length=100)
    secret = models.DateTimeField()
    active = models.CharField(max_length=1)


class Config_File(models.Model):
    class Meta:
        db_table = 'config_files'

    prod = models.ForeignKey('Product', related_name='configs')
    module = models.ForeignKey('Prod_Module', related_name='configs')
    filename = models.CharField(max_length=50)
    path = models.CharField(max_length=200)
    in_package = models.CharField(max_length=1)
    active = models.CharField(max_length=1)


class Configuration(models.Model):
    class Meta:
        db_table = 'configurations'

    type = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=200)
    configuration = models.TextField()
    param1 = models.CharField(max_length=100)
    param2 = models.CharField(max_length=100)
    active = models.CharField(max_length=1)


class DBC(models.Model):
    class Meta:
        db_table = 'database'

    server = models.ForeignKey('Dep_Server', related_name='dbs')
    type = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    db_host = models.CharField(max_length=200)
    db_name = models.CharField(max_length=50)
    db_port = models.CharField(max_length=5)
    db_user = models.CharField(max_length=20)
    db_pass = models.CharField(max_length=50)
    ssh_port = models.CharField(max_length=5)
    ssh_user = models.CharField(max_length=20)
    ssh_pass = models.CharField(max_length=50)
    ssh_key = models.CharField(max_length=200)


class Dep_Sql(models.Model):
    class Meta:
        db_table = 'dep_sql'

    prod = models.ForeignKey('Product', related_name='databases')
    database = models.CharField(max_length=50)
    db_type = models.CharField(max_length=6)
    db_name = models.CharField(max_length=50)
    db_host = models.CharField(max_length=50)
    db_port = models.CharField(max_length=5)
    db_user = models.CharField(max_length=20)
    db_pass = models.CharField(max_length=50)


class Dep_Action(models.Model):
    class Meta:
        db_table = 'dep_action'

    server_id = models.IntegerField()
    host_id = models.IntegerField()
    prod_id = models.IntegerField()
    sequence = models.IntegerField()
    operation = models.CharField(max_length=20)
    param1 = models.CharField(max_length=50)
    param2 = models.CharField(max_length=50)
    param3 = models.CharField(max_length=50)
    param4 = models.CharField(max_length=50)
    param5 = models.CharField(max_length=50)
    active = models.CharField(max_length=1, default='Y')


class Dep_Database(models.Model):
    class Meta:
        db_table = 'dep_database'

    server = models.ForeignKey('Dep_Server', related_name='databases')
    database = models.CharField(max_length=50)
    db_type = models.CharField(max_length=6)
    db_name = models.CharField(max_length=50)
    db_host = models.CharField(max_length=50)
    db_port = models.CharField(max_length=5)
    db_user = models.CharField(max_length=20)
    db_pass = models.CharField(max_length=50)


class Dep_Host(models.Model):
    class Meta:
        db_table = 'dep_host'

    server = models.ForeignKey('Dep_Server', related_name='hosts')
    host = models.CharField(max_length=100)
    ssh_port = models.CharField(max_length=5)
    ssh_user = models.CharField(max_length=20)
    ssh_pass = models.CharField(max_length=50)
    ssh_file = models.CharField(max_length=200)


class Dep_Log(models.Model):
    class Meta:
        db_table = 'dep_log'

    iid = models.IntegerField()
    user = models.IntegerField()
    time = models.DateTimeField()
    status = models.CharField(max_length=50)
    detail = models.TextField()


class Dep_Path(models.Model):
    class Meta:
        db_table = 'dep_path'

    host = models.ForeignKey('Dep_Host', related_name='paths')
    module = models.CharField(max_length=20)
    work_mod = models.CharField(max_length=10)
    src_name = models.CharField(max_length=50)
    des_path = models.CharField(max_length=100)
    des_name = models.CharField(max_length=50)


class Dep_Server(models.Model):
    class Meta:
        db_table = 'server'

    server = models.CharField(max_length=50)
    production = models.CharField(max_length=1)
    group = models.ForeignKey('User_Group')
    active = models.CharField(max_length=1)


class Dep_Status(models.Model):
    class Meta:
        db_table = 'dep_status'

    server = models.ForeignKey('Dep_Server')
    prod = models.ForeignKey('Product')
    branch = models.ForeignKey('Prod_Branch', related_name='builds')
    version = models.ForeignKey('Prod_Version')
    dep_user = models.ForeignKey('Auth', db_column='dep_user')
    dep_time = models.DateTimeField()
    description = models.TextField()
    dep_status = models.CharField(max_length=1)
    on_server = models.CharField(max_length=1)


class Execdb_Log(models.Model):
    class Meta:
        db_table = 'execdb_log'

    iid = models.IntegerField()
    user = models.IntegerField()
    time = models.DateTimeField()
    status = models.CharField(max_length=50)
    detail = models.TextField()


class Product(models.Model):
    class Meta:
        db_table = 'product'

    name = models.CharField(max_length=50)
    group = models.ForeignKey('User_Group')
    active = models.CharField(max_length=1)


class Prod_Branch(models.Model):
    class Meta:
        db_table = 'prod_branch'

    prod = models.ForeignKey('Product', related_name='branchs')
    branch = models.CharField(max_length=50)
    u = models.ForeignKey('Auth', related_name='branchs')
    git_branch = models.CharField(max_length=50)
    time = models.DateTimeField()


class Prod_BuildJobs(models.Model):
    class Meta:
        db_table = 'prod_buildjobs'

    prod = models.ForeignKey('Product', related_name='buildjobs')
    module = models.ForeignKey('Prod_Module', related_name='buildjobs')
    jenkins = models.ForeignKey('Prod_Jenkins', related_name='buildjobs')
    job_name = models.CharField(max_length=50)
    token = models.CharField(max_length=50)
    git_url = models.CharField(max_length=200)
    code_path = models.CharField(max_length=200)
    sql_path = models.CharField(max_length=200)
    mod = models.CharField(max_length=10)


class Prod_Builds(models.Model):
    class Meta:
        db_table = 'prod_builds'

    prod = models.ForeignKey('Product', related_name='builds')
    v = models.ForeignKey('Prod_Version', related_name='builds')
    bj = models.ForeignKey('Prod_BuildJobs', related_name='builds')
    q_id = models.CharField(max_length=20)
    b_id = models.CharField(max_length=20)
    status = models.CharField(max_length=1)
    rev = models.CharField(max_length=40)


class Prod_Jenkins(models.Model):
    class Meta:
        db_table = 'prod_jenkins'

    name = models.CharField(max_length=50)
    host = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=50)
    ssh_port = models.CharField(max_length=5)
    ssh_user = models.CharField(max_length=20)
    ssh_pass = models.CharField(max_length=30)
    ssh_key = models.CharField(max_length=100)
    storage = models.CharField(max_length=100)
    active = models.CharField(max_length=1)


class Prod_Module(models.Model):
    class Meta:
        db_table = 'prod_module'

    prod = models.ForeignKey('Product', related_name='modules')
    name = models.CharField(max_length=50)
    active = models.CharField(max_length=1)


class Prod_TestJob(models.Model):
    class Meta:
        db_table = 'prod_testjob'

    name = models.CharField(max_length=50)
    prod = models.ForeignKey('Product', related_name='testjobs')
    vid = models.IntegerField()
    server = models.ForeignKey('Dep_Server', related_name='testjobs')
    jenkins = models.ForeignKey('Prod_Jenkins', related_name='testjobs')
    job_name = models.CharField(max_length=50)
    token = models.CharField(max_length=50)
    active = models.CharField(max_length=1)


class Prod_TestJob_Param(models.Model):
    class Meta:
        db_table = 'prod_testjob_param'

    testjob = models.ForeignKey('Prod_TestJob', related_name='params')
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=100)


class Prod_Test(models.Model):
    class Meta:
        db_table = 'prod_test'

    prod = models.ForeignKey('Product', related_name='tests')
    version = models.ForeignKey('Prod_Version', related_name='tests')
    testjob = models.ForeignKey('Prod_TestJob', related_name='tests')
    server = models.ForeignKey('Dep_Server', related_name='tests')
    deploy = models.ForeignKey('Dep_Status', related_name='tests')
    q_id = models.CharField(max_length=20)
    b_id = models.CharField(max_length=20)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=1)
    output = models.CharField(max_length=200)


class Prod_Version(models.Model):
    class Meta:
        db_table = 'prod_version'

    prod = models.ForeignKey('Product', related_name='versions')
    branch = models.ForeignKey('Prod_Branch', related_name='versions')
    version = models.CharField(max_length=100)
    v_bn = models.IntegerField()
    code_v = models.CharField(max_length=32)
    conf_v = models.CharField(max_length=32)
    build_master = models.ForeignKey(Auth, related_name='builds', db_column='build_master')
    build_time = models.DateTimeField()
    descript = models.TextField()
    status = models.CharField(max_length=1)
    certified = models.CharField(max_length=1)


class User_Action(models.Model):
    class Meta:
        db_table = 'user_actions'

    user = models.ForeignKey(Auth, related_name='actions')
    time = models.DateTimeField()
    type = models.CharField(max_length=20)
    action = models.CharField(max_length=50)
    detail = models.TextField()
    extra_info = models.CharField(max_length=200)
    status = models.CharField(max_length=1)
    result = models.TextField()
    done_time = models.DateTimeField()


class User_Deleted_User(models.Model):
    class Meta:
        db_table = 'user_deleted_user'

    user_id = models.IntegerField(unique=True)
    username = models.CharField(max_length=20)
    email = models.CharField(max_length=100)
    display = models.CharField(max_length=100)


class User_Subscribe(models.Model):
    class Meta:
        db_table = 'user_subscribe'

    user = models.ForeignKey(Auth, related_name='focus')
    prod_id = models.IntegerField()
    server_id = models.IntegerField()
    deploy = models.CharField(max_length=1)
    test = models.CharField(max_length=1)


class User_Group(models.Model):
    class Meta:
        db_table = 'user_group'

    name = models.CharField(max_length=50)
    active = models.CharField(max_length=1)


class User_GroupPermission(models.Model):
    class Meta:
        db_table = 'user_group_permission'

    group = models.ForeignKey('User_Group', related_name='permissions')
    permission = models.ForeignKey('User_Permission', related_name='groups')


class User_Permission(models.Model):
    class Meta:
        db_table = 'user_permission'

    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20)
    action = models.CharField(max_length=10)
    description = models.CharField(max_length=200)
    value = models.CharField(max_length=50)
    active = models.CharField(max_length=1)


class User_UserGroup(models.Model):
    class Meta:
        db_table = 'user_user_group'

    user = models.ForeignKey('Auth', related_name='groups')
    group = models.ForeignKey('User_Group', related_name='users')


class User_UserPermission(models.Model):
    class Meta:
        db_table = 'user_user_permission'

    user = models.ForeignKey('Auth', related_name='permissions')
    permission = models.ForeignKey('User_Permission', related_name='users')


class AutoTest_Case(models.Model):
    class Meta:
        db_table = 'autotest_case'

    name = models.CharField(max_length=50)
    param = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    call_modle = models.CharField(max_length=200)
    active = models.CharField(max_length=1)


class AutoTest_action(models.Model):
    class Meta:
        db_table = 'autotest_action'

    name = models.CharField(max_length=50)
    temp = models.CharField(max_length=1)
    case_list = models.CharField(max_length=80)
    active = models.CharField(max_length=1)


class AutoTest_Job(models.Model):
    class Meta:
        db_table = 'autotest_job'

    test_job = models.CharField(max_length=50)
    prod = models.ForeignKey('Product', related_name='autotest_job')
    server = models.ForeignKey('Dep_Server', related_name='autotest_job')


class User_Exec_Shell(models.Model):
    class Meta:
        db_table = 'user_exec_shell'

    user = models.ForeignKey('Auth', related_name='user_shell')
    host = models.ForeignKey('Dep_Host', related_name='host_shell')
    shell = models.CharField(max_length=80)


class Config_Path(models.Model):
    class Meta:
        db_table = 'config_path'

    pconf = models.ForeignKey('Config_File', related_name='pconfigs')
    dpath = models.ForeignKey('Dep_Path', related_name='dpaths')
    path = models.CharField(max_length=50)
    in_package = models.CharField(max_length=1, default='Y')
    active = models.CharField(max_length=1, default='Y')
