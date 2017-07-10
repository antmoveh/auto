from django.http import HttpResponse
from .pages.about import ABOUT_PAGE
from .pages.build import BUILD_PAGE
from .pages.configuration import CONFIG_PAGE
from .pages.deploy import DEPLOY_PAGE
from .pages.execdb import EXECDB_PAGE
from .pages.index import INDEX_PAGE
from .pages.manage import MANAGE_PAGE
from .pages.server import SERVER_PAGE
from .pages.tools import TOOLS_PAGE
from .pages.user import USER_PAGE
from .pages.test import TEST_PAGE
from .pages.user_group import USER_GROUP_PAGE

web_pages = {
'about': ABOUT_PAGE,
'build': BUILD_PAGE,
'configuration': CONFIG_PAGE,
'deploy': DEPLOY_PAGE,
'dbc': EXECDB_PAGE,
'index': INDEX_PAGE,
'manage': MANAGE_PAGE,
'server': SERVER_PAGE,
'tools': TOOLS_PAGE,
'user': USER_PAGE,
'test': TEST_PAGE,
'user_group': USER_GROUP_PAGE,
}


def index(request):
    GET = request.GET
    mod = 'index'
    if 'm' in GET:
        if GET.get('m') in web_pages:
            mod = GET.get('m')
    if mod in web_pages:
        page_type = web_pages[mod]
        page = page_type(request, mod)
        render = page.render(request)
        return render
    return HttpResponse()

# return render_to_response('index.html', {'title': 'Test index.html', 'body': 'Test home page.', 'tabs': UI.generate_tabs(mod)})
