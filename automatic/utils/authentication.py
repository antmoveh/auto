import conf
from automatic.models import *


class Authentication():
    def __init__(self, uid):
        try:
            self.uid = int(uid)
        except Exception as e:
            return False
        self.permissions = self.get_user_permission()

    def get_user_permission(self):
        try:
            user = Auth.objects.get(id=self.uid)
        except Exception as e:
            return None
        permissions = {}
        if user.active == 'Y':
            u_p_rs = User_UserPermission.objects.filter(user=user)
            for u_p_r in u_p_rs:
                u_p = u_p_r.permission
                if u_p.active == 'Y' and u_p.type not in permissions:
                    permissions[u_p.type] = {}
                permissions[u_p.type][u_p.action] = [u_p.id, u_p.action, u_p.value]
        # user_groups = User_UserGroup.objects.filter(user = user)
        # for group in user_groups:
        # g_p_rs = User_GroupPermission.objects.filter(group = group)
        # for g_p_r in g_p_rs:
        # g_p = g_p_r.permission
        # if g_p.active == 'Y' and g_p.type not in permissions:
        # permissions[g_p.type] = {g_p.action: [g_p.id, g_p.action, g_p.value]}
        # else:
        #				if g_p.action not in permissions[g_p.type]:
        #					permissions[g_p.type][g_p.action] = [g_p.id, g_p.action, g_p.value]
        return permissions

    def verify_action(self, type, action):
        if type in self.permissions:
            if action in self.permissions[type]:
                return True
        return False

    @staticmethod
    def verify_group(request):
        if 'login' in request.session and request.session['login']:
            if 'uid' in request.session:
                uid = request.session['uid']
            else:
                uid = conf.USER_ANONYMOUS
            try:
                auth = Auth.objects.get(id=uid)
                user_group = User_UserGroup.objects.get(user=auth)
                return user_group.group_id
            except Exception as e:
                print(e)
                return 0

