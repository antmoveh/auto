import json
import os
import shutil
import traceback
import conf

from automatic.utils.email import mail_attach
from automatic.utils.file import UploadFileForm
from automatic.utils.file import handle_uploaded_file
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
from automatic.models import *
from .webpage import WEBPAGE


class TEST_PAGE(WEBPAGE):
    template = 'pages/test.html'
    server_id = None

    def __init__(self, request, type=None):
        if 'sid' in request.GET:
            self.server_id = request.GET.get('sid')
        super().__init__(request, type)

    def render(self, request):
        title, tab_list = self.generate_nav_tabs(self.type)
        uid, username, login = self.render_user(request)
        return render_to_response(self.template,
                                  {'title': title, 'tabs': tab_list, 'login': login, 'uid': uid, 'username': username})

    @staticmethod
    def get_caselist(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        cls = []
        try:
            act = AutoTest_Case.objects.all()
            for ac in act:
                cl = [ac.id, ac.name, ac.description, ac.param, ac.call_modle]
                cls.append(cl)
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取用例信息出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': cls}))

    @staticmethod
    def edit_case(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        try:
            r = request.POST.get("request")
            j = json.loads(r)
            cid = int(j["cid"])
            cname = j["cname"]
            if cname == "" or cname is None:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '用例名不能为空'}))
            description = j["description"]
            cparam = j["cparam"]
            ccall = j["ccall"]
            atc = AutoTest_Case.objects.all()
            if cid == 0:
                for at in atc:
                    if at.name == cname:
                        return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '用例名已存在'}))
                atc1 = AutoTest_Case(name=cname, description=description, param=cparam, call_modle=ccall, active='Y')
                atc1.save()
            else:
                atc2 = AutoTest_Case.objects.get(id=cid)
                index = 0
                for at in atc:
                    if at.name == cname and atc2.name != cname:
                        index += 1
                if index == 0:
                    if atc2.name != cname:
                        atc2.name = cname
                    if atc2.description != description:
                        atc2.description = description
                    if atc2.param != cparam:
                        atc2.param = cparam
                    if atc2.call_modle != ccall:
                        atc2.call_modle = ccall
                    atc2.save()
                else:
                    return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '更改后的用例名已存在'}))
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '更新用例信息出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': "更新成功"}))

    @staticmethod
    def delete_case(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        cid = request.GET.get("cid")
        try:
            act = AutoTest_Case.objects.get(id=cid)
            act.delete()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '删除用例出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': "删除成功"}))

    @staticmethod
    def get_test_conf(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        cid = None
        if 'cid' in request.GET:
            try:
                cid = int(request.GET.get('cid'))
            except:
                pass
        try:
            action_list = AutoTest_action.objects.all()
            confs = []
            for action in action_list:
                confs.append([action.id, action.name])
            try:
                conf = AutoTest_action.objects.get(id=cid)
                confs_info = {'id': conf.id, 'name': conf.name, 'temp': conf.temp, 'case_list': conf.case_list}
            except Exception as e:
                confs_info = {}
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取测试配置信息出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (
                True, json.JSONEncoder().encode({'status': 'OK', 'msg': {'confs': confs, 'confs_info': confs_info}}))

    @staticmethod
    def delete_conf(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        if 'cid' in request.GET:
            cid = int(request.GET.get('cid'))
        try:
            conf_ = AutoTest_action.objects.get(id=cid)
            conf_.delete()
            file = conf.settings_autotestfile_location + str(cid)
            if os.path.isdir(file):
                shutil.rmtree(file, True)
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '删除配置出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '删除成功'}))

    @staticmethod
    def submit_action(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        try:
            r = request.POST.get('request')
            j = json.loads(r)
            cid = int(j['cid'])
            cname = j['cname']
            case_list = j['case_list']
            if int(cid) == 0:
                ata = AutoTest_action.objects.all()
                for at in ata:
                    if cname == at.name:
                        return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '已存在任务名称'}))
                conf_ = AutoTest_action(name=cname, temp='N', case_list=case_list, active='Y')
            else:
                conf_ = AutoTest_action.objects.get(id=cid)
                if cname != conf_.name:
                    conf_.name = cname
                if case_list != conf_.case_list:
                    conf_.case_list = case_list
                    if case_list != '':
                        c_l = case_list[:-1].split(',')
                        param = open(conf.settings_autotestfile_location + str(conf_.id) + '/param', 'w')
                        for i in range(len(c_l)):
                            p = AutoTest_Case.objects.get(id=c_l[i])
                            param.write('usercase=' + p.name + '\n')
                            param.write(p.param + '\n')
                            param.write('model=N' + '\n')
                            param.write('model_name=' + '\n')
                            param.write('-----------------------------------------\n')
                        param.close()
            conf_.save()
            file = conf.settings_autotestfile_location + str(conf_.id)
            if not os.path.isdir(file):
                os.mkdir(file)
                if case_list != '':
                    c_l = case_list[:-1].split(',')
                    param = open(conf.settings_autotestfile_location + str(conf_.id) + '/param', 'w')
                    for i in range(len(c_l)):
                        p = AutoTest_Case.objects.get(id=c_l[i])
                        param.write('usercase=' + p.name + '\n')
                        param.write(p.param + '\n')
                        param.write('model=N' + '\n')
                        param.write('model_name=' + '\n')
                        param.write('-----------------------------------------\n')
                    param.close()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '提交测试任务出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': {'cid': conf_.id}}))


    @staticmethod
    def submit_area(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        try:
            r = request.POST.get('request')
            j = json.loads(r)
            cid = int(j['cid'])
            para = j['text']
            if int(cid) == 0:
                atp = conf.settings_autotestfile_location + 'temp/param'
            else:
                atp = conf.settings_autotestfile_location + str(cid) + '/param'
            param = open(atp, 'w')
            param.write(para)
            param.close()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '保存参数出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '提交成功'}))

    @staticmethod
    def deploy_submit_area(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        try:
            r = request.POST.get('request')
            j = json.loads(r)
            file = j['file']
            para = j['text']
            atp = conf.settings_autotestfile_location + file + '/param'
            param = open(atp, 'w')
            param.write(para)
            param.close()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '保存参数出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '提交成功'}))

    @staticmethod
    def manage_submit_area(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        try:
            r = request.POST.get('request')
            j = json.loads(r)
            sid = int(j['sid'])
            pid = int(j['pid'])
            para = j['text']
            atp = conf.settings_autotestfile_location + str(pid) + '_' + str(sid) + '/param'
            param = open(atp, 'w')
            param.write(para)
            param.close()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '保存参数出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '提交成功'}))

    @staticmethod
    def show_para(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        try:
            cid = int(request.GET.get('cid'))
            try:
                case_list = request.GET.get('case_list')
            except:
                case_list = ''
            if cid == 0 and case_list is not None:
                atp = conf.settings_autotestfile_location + 'temp/param'
                if case_list != '':
                    c_l = case_list[:-1].split(',')
                    param = open(atp, 'w')
                    for i in range(len(c_l)):
                        p = AutoTest_Case.objects.get(id=c_l[i])
                        param.write('usercase=' + p.name + '\n')
                        param.write(p.param + '\n')
                        param.write('model=N' + '\n')
                        param.write('model_name=' + '\n')
                        param.write('-----------------------------------------\n')
                    param.close()
            else:
                atp = conf.settings_autotestfile_location + str(cid) + '/param'
            text = ''
            if os.path.isfile(atp):
                param = open(atp, 'r')
                text = param.read()
                param.close()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取参数出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': text}))

    @staticmethod
    def upload_file(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        try:
            cid = request.POST.get('file_pid')
            if int(cid) == 0:
                cid = 'temp'
            if request.method == 'POST':
                form = UploadFileForm(request.POST, request.FILES)
                if form.is_valid():
                    handle_uploaded_file(request.FILES['file'], cid)
                else:
                    return HttpResponse(u'非POST请求')
        except Exception as e:
            return HttpResponse(u'上传失败:' + str(e))
        else:
            return cid

    @staticmethod
    def check_testcase(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        try:
            cid = request.GET.get('cid')
            if int(cid) == 0:
                at = conf.settings_autotestfile_location + 'temp/'
            else:
                at = conf.settings_autotestfile_location + str(cid) + '/'
            file_list = os.listdir(at)
            file = ''
            if int(len(file_list)) == 0:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '不存在专属用例'}))
            elif int(len(file_list)) > 0:
                for file_l in file_list:
                    file += file_l + '<br />'
            else:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '不存在专属用例'}))
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '执行出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': file}))

    @staticmethod
    def datacollection(action='default', param_path=None, case_list=None):
        try:
            if case_list.endswith(','):
                case_list = case_list[:-1]
            case_list = case_list.split(',')
            err = '详细结果请参考附件\n'
            result_list = []
            # 创建测试用例对象
            for i in range(len(case_list)):
                try:
                    atc = AutoTest_Case.objects.get(id=case_list[i])
                    scope = {'param_path': param_path}
                    exec(atc.call_modle, scope)
                    result_list.append(scope['r_l'])
                    result_list.append(scope['r_l_e'])
                except Exception as e:
                    err += str(e) + '\n'
        except Exception as e:
            return (action, result_list, err)
        else:
            return (action, result_list, err)


    @staticmethod
    def submit_show_param(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        sid = request.GET.get('sid')
        pid = request.GET.get('pid')
        if 'job' in request.GET:
            job = request.GET.get('job')
        else:
            job = ''
        try:
            server = Dep_Server.objects.get(id=sid)
            prod = Product.objects.get(id=pid)
            try:
                atj = AutoTest_Job.objects.filter(prod=prod, server=server)[0]
            except IndexError as e:
                atj = None
            if atj is not None:
                if job != atj.test_job:
                    atj.test_job = job
                    if job != '':
                        j = job[:-1].split(',')
                        param = open(conf.settings_autotestfile_location + str(pid) + '_' + str(sid) + '/param', 'w')
                        for i in range(len(j)):
                            _j = AutoTest_action.objects.get(id=j[i])
                            param.write('TEST_TASK=' + _j.name + '\n')
                            p_j = open(conf.settings_autotestfile_location + str(j[i]) + '/param', 'r')
                            text = p_j.read()
                            param.write(text)
                            p_j.close()
                        param.close()
            else:
                atj = AutoTest_Job(prod=prod, server=server, test_job=job)
            atj.save()
            file = conf.settings_autotestfile_location + str(pid) + '_' + str(sid)
            if not os.path.isdir(file):
                os.mkdir(file)
                if job != '':
                    j = job[:-1].split(',')
                    param = open(conf.settings_autotestfile_location + str(pid) + '_' + str(sid) + '/param', 'w')
                    for i in range(len(j)):
                        _j = AutoTest_action.objects.get(id=j[i])
                        param.write('TEST_TASK=' + _j.name + '\n')
                        p_j = open(conf.settings_autotestfile_location + str(j[i]) + '/param', 'r')
                        text = p_j.read()
                        param.write(text)
                        p_j.close()
                    param.close()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '执行出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '保存成功'}))

    @staticmethod
    def show_param(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        sid = request.GET.get('sid')
        pid = request.GET.get('pid')
        try:
            file = conf.settings_autotestfile_location + str(pid) + '_' + str(sid) + '/param'
            param = open(file, 'r')
            text = param.read()
            param.close()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '执行出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': text}))

    @staticmethod
    def deploy_show_param(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        file_ = request.GET.get('file')
        try:
            file = conf.settings_autotestfile_location + file_ + '/param'
            param = open(file, 'r')
            text = param.read()
            param.close()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '执行出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': text}))

    @staticmethod
    def get_script_task(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        try:
            atas = AutoTest_action.objects.all()
            atcs = AutoTest_Case.objects.all()
            aaction = []
            acase = []
            for ata in atas:
                aaction.append([ata.id, ata.name])
            for atc in atcs:
                acase.append([atc.id, atc.name])
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '执行出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': {'aaction': aaction, 'acase': acase}}))

    @staticmethod
    def show_action_param(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        try:
            task_list = request.GET.get('task_list')
            j = task_list[:-1].split(',')
            param = open(conf.settings_autotestfile_location + 'task/param', 'w')
            for i in range(len(j)):
                _j = AutoTest_action.objects.get(id=j[i])
                param.write('TEST_TASK=' + _j.name + '\n')
                p_j = open(conf.settings_autotestfile_location + str(j[i]) + '/param', 'r')
                text = p_j.read()
                param.write(text)
                p_j.close()
            param.close()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '执行出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '保存成功'}))

    @staticmethod
    def show_case_param(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        try:
            case_list = request.GET.get('case_list')
            atp = conf.settings_autotestfile_location + 'case/param'
            c_l = case_list[:-1].split(',')
            param = open(atp, 'w')
            for i in range(len(c_l)):
                p = AutoTest_Case.objects.get(id=c_l[i])
                param.write('usercase=' + p.name + '\n')
                param.write(p.param + '\n')
                param.write('model=N' + '\n')
                param.write('model_name=' + '\n')
                param.write('-----------------------------------------' + '\n')
            param.close()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '执行出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '保存成功'}))

    @staticmethod
    def show_result_list(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        cid = request.GET.get('cid')
        try:
            if int(cid) == 0:
                last_path = conf.settings_autotestfile_location + 'temp/last'
            else:
                last_path = conf.settings_autotestfile_location + str(cid) + '/last'
            if not os.path.isfile(last_path):
                os.mknod(last_path)
                result_list = []
            else:
                last = open(last_path, 'r')
                result_list = last.read()
                last.close()
                result_list = result_list.split(';')
                while '' in result_list:
                    result_list.remove('')
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '执行出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': result_list}))

    @staticmethod
    def show_result(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        cid = request.GET.get('cid')
        name = request.GET.get('name')
        try:
            if int(cid) == 0:
                result_path = conf.settings_autotestfile_location + 'temp/' + name
            else:
                result_path = conf.settings_autotestfile_location + str(cid) + '/' + name
            if not os.path.isfile(result_path):
                result_content = '结果文件不存在'
            else:
                result = open(result_path, 'r')
                result_content = result.read()
                result.close()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '执行出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': result_content}))


    @staticmethod
    def deploy_run_case(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        uid = conf.USER_ANONYMOUS
        if 'uid' in request.session:
            uid = request.session['uid']
        try:
            auth = Auth.objects.get(id=uid)
            file = request.GET.get('file')
            t = str(request.GET.get('t'))
            result_list_all = []
            param_path = ''
            if file == 'task':
                param_path = conf.settings_autotestfile_location + 'task'
                if t.endswith(','):
                    t = t[:-1]
                task_list = t.split(',')
                for i in range(len(task_list)):
                    ata = AutoTest_action.objects.get(id=task_list[i])
                    case_list = ata.case_list
                    if case_list != '':
                        action_name, result_list, err = TEST_PAGE.datacollection('deploy', param_path, case_list)
                        for j in range(len(result_list)):
                            result_list_all.append(result_list[j])
            elif file == 'case':
                param_path = conf.settings_autotestfile_location + 'case'
                action_name, result_list, err = TEST_PAGE.datacollection('deploy', param_path, t)
                result_list_all = result_list
            else:
                pass
            mail_attach(subject=action_name + '测试完成', body=err, from_mail='bsp-auto@kokozu.net', to_mail=[auth.email],
                        cc=None, file_location=param_path, result_list=result_list_all)
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '执行出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '执行完成请查收邮件'}))


    @staticmethod
    def execute_action(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP请求出错'}))
        uid = conf.USER_ANONYMOUS
        if 'uid' in request.session:
            uid = request.session['uid']
        cid = request.GET.get('cid')
        try:
            case_list = request.GET.get('case_list')
        except:
            case_list = ''
        try:
            action = 'default'
            if int(cid) == 0 and case_list is None or case_list == '':
                return ('FAILED', '', '请选择用例')
            elif int(cid) == 0 and case_list is not None:
                case_list = case_list
                param_path = conf.settings_autotestfile_location + 'temp'
                action = '临时任务'
            else:
                ata = AutoTest_action.objects.get(id=cid)
                case_list = ata.case_list
                param_path = conf.settings_autotestfile_location + str(cid)
                action = ata.name
            auth = Auth.objects.get(id=uid)
            action_name, result_list, err = TEST_PAGE.datacollection(action, param_path, case_list)
            file_location = conf.settings_autotestfile_location + str(cid) + '/'
            if int(cid) == 0:
                file_location = conf.settings_autotestfile_location + 'temp/'
            print(result_list)
            last = open(file_location + 'last', 'w')
            last.write(';'.join(result_list))
            last.close()
            mail_attach(subject=action_name + '测试完成', body=err, from_mail='bsp-auto@kokozu.net', to_mail=[auth.email],
                        cc=None, file_location=file_location, result_list=result_list)
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '执行出错：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'OK', 'msg': '执行完成请查收邮件'}))


    @staticmethod
    def start_test(server, prod):
        try:
            atj = AutoTest_Job.objects.filter(server=server, prod=prod)[0]
        except IndexError as e:
            return '没有配置自动化测试任务'
        if atj.test_job != '':
            param_path = conf.settings_autotestfile_location + str(atj.prod) + '_' + str(atj.server)
            test_list = atj.test_job
            if test_list.endswith(','):
                test_list = test_list[:-1]
            test_list = test_list.split(',')
            result_list_all = []
            for i in range(len(test_list)):
                ata = AutoTest_action.objects.get(id=test_list[i])
                case_list = ata.case_list
                if case_list != '':
                    action_name, result_list, err = TEST_PAGE.datacollection('deploy', param_path, case_list)
                    for j in range(len(result_list)):
                        result_list_all.append(str(atj.prod) + '_' + str(atj.server) + '/' + result_list[j])
            deploy = Dep_Status.objects.filter(server=server, prod=prod, on_server='Y').order_by('-id')[0]
            subscribes = User_Subscribe.objects.filter(prod_id__in=[0, prod.id], server_id__in=[0, server.id], test='Y')
            cc = []
            for s in subscribes:
                cc.append(s.user.email)
            cc = list(set(cc))
            if deploy.dep_user.email in cc:
                cc.remove(deploy.dep_user.email)
            file_location = conf.settings_autotestfile_location
            mail_attach(subject=deploy.prod.name + '测试完成', body=err, from_mail='bsp-auto@kokozu.net',
                        to_mail=[deploy.dep_user.email], cc=cc, file_location=file_location,
                        result_list=result_list_all)

