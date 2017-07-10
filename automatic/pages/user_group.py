# coding:utf8
import json
import traceback

from django.shortcuts import render_to_response
from automatic.models import *
from .webpage import WEBPAGE


class USER_GROUP_PAGE(WEBPAGE):
    template = 'pages/user_group.html'

    def __init__(self, request, type=None):
        super().__init__(request, type)

    def render(self, request):
        title, tab_list = self.generate_nav_tabs(self.type)
        uid, username, login = self.render_user(request)
        return render_to_response(self.template,
                                  {'title': title, 'tabs': tab_list, 'login': login, 'uid': uid, 'username': username})

    @staticmethod
    def load_data(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        try:
            group = {}
            user_group = {}
            auths = Auth.objects.all()
            ugs = User_Group.objects.all()
            for ug in ugs:
                __uug = []
                if ug.id == 2:
                    for auth in auths:
                        if auth.groups.count() == 0 and auth.id != 2 and auth.id != 3:
                            __uug.append([auth.id, auth.display])
                uugs = User_UserGroup.objects.filter(group=ug)
                for uug in uugs:
                    __uug.append([uug.user.id, uug.user.display])
                group[ug.id] = ug.name
                user_group[ug.id] = __uug
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '获取分组失败：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (
                True, json.JSONEncoder().encode({'status': 'NEW', 'msg': {'group': group, 'user_group': user_group}}))

    @staticmethod
    def add_group(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        try:
            group_name = request.GET.get('gn')
            ugs = User_Group.objects.all()
            for ug in ugs:
                if ug.name == group_name:
                    return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '已存在分组名'}))
            u = User_Group(name=group_name, active='Y')
            u.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '添加分组失败：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'NEW', 'msg': '添加成功'}))

    @staticmethod
    def delete_group(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        try:
            gid = int(request.GET.get('gid'))
            if gid == 1 or gid == 2:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '该组不允许删除'}))
            ug = User_Group.objects.get(id=gid)
            uug = User_UserGroup.objects.filter(group=ug)
            if uug.count() == 0:
                ug.delete()
            else:
                return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': '该组下存在用户'}))
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '删除失败：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'NEW', 'msg': '删除成功'}))

    @staticmethod
    def move_user(request):
        if request is None:
            return (False, json.JSONEncoder().encode({'status': 'FAILED', 'msg': 'HTTP request失效'}))
        try:
            uid = request.GET.get('uid')
            gid = request.GET.get('gid')
            try:
                uug = User_UserGroup.objects.get(user_id=uid)
                if uug.group.id == gid:
                    pass
                else:
                    ug = User_Group.objects.get(id=gid)
                    uug.group = ug
                    uug.save()
            except Exception as e:
                u = Auth.objects.get(id=uid)
                g = User_Group.objects.get(id=gid)
                ugx = User_UserGroup(user=u, group=g)
                ugx.save()
        except Exception as e:
            return (False, json.JSONEncoder().encode(
                {'status': 'FAILED', 'msg': '移动失败：\n' + str(e) + '\n' + traceback.format_exc()}))
        else:
            return (True, json.JSONEncoder().encode({'status': 'NEW', 'msg': '移动成功'}))

