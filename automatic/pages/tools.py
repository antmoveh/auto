from django.shortcuts import render_to_response
from .webpage import WEBPAGE


class TOOLS_PAGE(WEBPAGE):
    template = 'pages/tools.html'

    def __init__(self, request, type=None):
        super().__init__(request, type)

    def render(self, request):
        title, tab_list = self.generate_nav_tabs(self.type)
        uid, username, login = self.render_user(request)
        return render_to_response(self.template,
                                  {'title': title, 'tabs': tab_list, 'login': login, 'uid': uid, 'username': username})
