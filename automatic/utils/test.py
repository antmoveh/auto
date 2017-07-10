import datetime
import traceback
import automatic.utils.email as EMAIL
from .config import Config
from .jenkins import *
from automatic.models import *


def new_test(jid):
    job = Prod_TestJob.objects.get(id=jid)
    prod = job.prod
    server = job.server
    deploy = Dep_Status.objects.filter(server=server, prod=prod, on_server='Y').order_by('-id')[0]
    version = deploy.version
    now = datetime.datetime.now()
    test = Prod_Test(prod=prod, version=version, testjob=job, server=server, deploy=deploy, q_id='', b_id='',
                     start_time=now, end_time=now, status='W', output='')
    test.save()
    tid = test.id
    params = job.params.all()
    jenkins_server = job.jenkins
    jenkins = Jenkins(url=jenkins_server.url, username=jenkins_server.username, password=jenkins_server.password)
    p = {'id': str(tid), 'bsp': Config.get_config('env', 'bsp_url')['value']}
    for param in params:
        p[param.key] = param.value
    jenkins_q_id = jenkins.build_job(job.job_name, parameters=p, token=job.token)
    test.q_id = jenkins_q_id
    test.save()


def test_start(request):
    if request is None:
        return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': 'HTTP request is None.'}))
    if 'id' not in request.GET:
        return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': '未指定测试任务'}))
    if 'jid' not in request.GET:
        return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': '未提供jenkins任务序号'}))
    try:
        tid = int(request.GET.get('id'))
        b_id = request.GET.get('jid')
        test = Prod_Test.objects.get(id=tid)
        test.start_time = datetime.datetime.now()
        test.b_id = b_id
        test.status = 'T'
        test.save()
    except Exception as e:
        return (False, json.JSONEncoder().encode(
            {'status': 'Failed', 'msg': 'Error: \n' + str(e) + '\n' + traceback.format_exc()}))
    return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': 'Test status updated: STARTED'}))


def test_end(request):
    if request is None:
        return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': 'HTTP request is None.'}))
    if 'id' not in request.GET:
        return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': '未指定测试任务'}))
    try:
        tid = int(request.GET.get('id'))
        test = Prod_Test.objects.get(id=tid)
        test.end_time = datetime.datetime.now()
        test.status = 'Y'
        test.save()
        check_test_end(test.deploy)
    except Exception as e:
        return (False, json.JSONEncoder().encode(
            {'status': 'Failed', 'msg': 'Error: \n' + str(e) + '\n' + traceback.format_exc()}))
    return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': 'Test status updated: FINISHED'}))


def test_failed(request):
    if request is None:
        return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': 'HTTP request is None.'}))
    if 'id' not in request.GET:
        return (False, json.JSONEncoder().encode({'status': 'Failed', 'msg': '未指定测试任务'}))
    try:
        tid = int(request.GET.get('id'))
        test = Prod_Test.objects.get(id=tid)
        test.end_time = datetime.datetime.now()
        test.status = 'F'
        test.save()
        check_test_end(test.deploy)
    except Exception as e:
        return (False, json.JSONEncoder().encode(
            {'status': 'Failed', 'msg': 'Error: \n' + str(e) + '\n' + traceback.format_exc()}))
    return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': 'Test status updated: FAILED'}))


def check_test_end(deploy):
    if deploy is None:
        return None
    tz_diff = datetime.timedelta(hours=8)
    test_result = []
    prod = deploy.prod
    server = deploy.server
    version = deploy.version
    jobs = Prod_TestJob.objects.filter(prod=prod, server=server, active='Y')
    for j in jobs:
        jenkins = j.jenkins.url
        if jenkins[-1] != '/':
            jenkins += '/'
        test = Prod_Test.objects.filter(testjob=j).order_by('-id')
        if len(test) > 0:
            test = test[0]
            if test.status in ['W', 'T']:
                # return False
                continue
            if test.status == 'Y':
                status = '<font color=\"green\">测试通过</font>'
            elif test.status == 'F':
                status = '<font color=\"red\">测试失败</font>'
            else:
                status = test.status
            start_time = str(test.start_time + tz_diff)
            end_time = str(test.end_time + tz_diff)
            url = jenkins + 'job/' + j.job_name + '/' + test.b_id + '/console'
            test_result.append(
                {'name': j.name, 'status': status, 'start_time': start_time, 'end_time': end_time, 'url': url})
    subject = '测试完成: ' + prod.name + ' ' + version.version + ' 于 ' + server.server
    context = {'prod': prod.name, 'version': version.version, 'server': server.server, 'tests': test_result,
               'user': deploy.dep_user.display, 'dep_time': str(deploy.dep_time + tz_diff)}
    subscribes = User_Subscribe.objects.filter(prod_id__in=[0, prod.id], server_id__in=[0, server.id], test='Y')
    cc = []
    for s in subscribes:
        cc.append(s.user.email)
    cc = list(set(cc))
    if deploy.dep_user.email in cc:
        cc.remove(deploy.dep_user.email)
    EMAIL.mail(subject=subject, mode='test', html_context=context, to_mail=[deploy.dep_user.email], cc=cc,
               text_content=subject)
