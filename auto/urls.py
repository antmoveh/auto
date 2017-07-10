from django.conf.urls import url
from django.views.generic.base import RedirectView

# from django.contrib import admin
from automatic import action, autotest, views

urlpatterns = [
    url(r'^favicon.ico', RedirectView.as_view(url='/static/pages/img/favicon.ico')),
    url(r'^$', views.index),
    url(r'^action/$', action.action),
    url(r'^build/$', action.build),
    url(r'^login/$', action.login),
    url(r'^user/$', action.user),
    url(r'^view/$', action.view),
    url(r'^test/$', action.test),
    url(r'^user_group/$', autotest.user_group),
    url(r'^autotest/$', autotest.action),
    url(r'^autotest_login/$', autotest.action_login),
    url(r'^hint_login/$', autotest.hint_login),
    url(r'^autotest_script/$', autotest.auto_script_main),
    url(r'^autotest/upload/$', autotest.upload),
]

