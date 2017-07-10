import django

django.setup()
import datetime
from automatic.utils.build import *
from automatic.utils.jenkins import *
from automatic.utils.build import *
import paramiko


def main():
    print(datetime.datetime.now())
    transport = paramiko.Transport(('114.215.130.32', 35862))
    pk = paramiko.RSAKey.from_private_key_file('/data/applications/auto/id_rsa')
    transport.connect(username='kdy_yanfa', pkey=pk)
    # ssh = SSHHelper(hostname = '114.215.130.32', port = 35862, username = 'kdy_yanfa', password = 'abc', key_file = '/data/applications/auto/id_rsa')
    # print(ssh.run_command('ls'))
    # xml = JENKINS_XML()
    # xml.generate_default()
    # set = SETTINGS('data', 2, 4)
    # set.get_combined_file(common = '/data/applications/workspace/git/configurations/data/application.properties__0', host = '/data/applications/workspace/git/configurations/data/application.properties__2', combined = '/home/auto/combined.cfg')
    # build = Build(prod_id = 1, branch_id = 2)
    # build.new_build()
    # root = ET.fromstring(test_xml)
    # if root.tag == 'leftItem':
    # print('Build done.')
    # b_job = root.find('./task/name').text
    # 	b_bn = root.find('./executable/number').text
    # 	print(b_job + ': ' + b_bn)
    # elif root.tag == 'waitingItem':
    # 	print('Waiting in Queue.')
    # else:
    # 	print(root.tag)
    # jenkins = Jenkins('http://121.40.54.130:1080/')
    # info = jenkins.get_info()
    # print(info)
    # v = jenkins.build_job(name = 'test', parameters = {'a': 'aa', 'b': 'bb'}, token = 'KoK0ZuIZ3')
    # print(v)
    # print(jenkins.get_q_item_url(v))
    # print(ssh.run_command('ls'))
    # navigation = Config()['ui_nav']
    # nav_index = list(navigation.keys())
    # nav_index.sort()
    # tab_list = []
    # for index in nav_index:
    # 	tab_list.append(navigation[index]['value'])
    # print(tab_list)
    # parser = argparse.ArgumentParser(description = 'Argument Parser')
    # parser.add_argument('--server', '-s', type = str)
    # args = vars(parser.parse_args())
    # print(args)
    # log = LOG('DEPLOY')
    # s_name = 'dev'
    # if ('server' in args) and (args['server'] != None) and (len(args['server'] > 0)):
    # 	s_name = args['server']
    # deploy = DEPLOY(s_name = s_name)
    # s_id = 2
    # deploy2 =DEPLOY(s_id = s_id)
    # print(deploy.server.server_name)
    # print(deploy.server.server_host)
    # print(deploy2.server.server_name)
    # print(deploy2.server.server_host)
    # deploy.deploy()
    # EMAIL.mail('a', 'Test mail', 'This is a test.', [])
    # f = open('/data/applications/workspace/test/common', 'r')
    # common_lines = f.readlines()
    # f.close()
    # f = open('/data/applications/workspace/test/host', 'r')
    # host_lines = f.readlines()
    # f.close()
    # combined = settings.combine_settings(common_lines, host_lines)
    # f = open('/data/applications/workspace/test/combined', 'w')
    # f.writelines(combined)
    # f.close()
    # log_general = LOG()
    # log_deploy = LOG('dep')
    # log_general.info('test log 1 info')
    # log_general.warning('test log 1 warning')
    # log_deploy.warning('test log 2 warning')
    # log_deploy.error('test log 2 error')
    # sshhelper = SSHHelper(hostname = '121.40.54.130', port = 34846, username = 'auto', password = 'daYtona500')
    # sshhelper.run_command('ls -l /data')
    # del sshhelper
    # config = Config()
    # config.display_configurations()
    # print(config['env'])
    # print(config['env']['log_file']['value'])
    # print(config['env']['log_file']['configuration'])
    # utc_time = datetime.datetime.utcnow()
    # timestamp = calendar.timegm(utc_time.timetuple()) + utc_time.microsecond / 1000000
    # time_id = str(timestamp * 1000000)
    # item = {'ilvl': 'INFO', 'utc_time': utc_time, 'timestamp': timestamp, 'time_id': time_id, 'module': None, 'log_content': 'test content'}
    # test([item])
    print(datetime.datetime.now())


if __name__ == "__main__":
    main()
