__author__ = 'drlemur'

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.index,name='exp_index'),
    url(r'^group/(?P<groupToken>[0-9a-z]+)$', views.get_session, name='get_session'),
    url(r'^group/(?P<groupToken>[0-9a-z]+)/(?P<workerId>[0-9a-zA-Z_]+)$', views.get_session, name='get_session'),
    url(r'^start/(?P<sessionToken>[0-9a-z]+)$', views.start, name='start_exp'),
    url(r'^start/(?P<sessionToken>[0-9a-z]+)/(?P<args>[0-9a-zA-Z]+)$', views.start, name='start_exp'),
    url(r'^consent/(?P<sessionToken>[0-9a-z]+)', views.get_consent, name='get_consent'),
    url(r'^report/(?P<sessionToken>[0-9a-z]+)', views.report, name='report_exp'),
    url(r'^experiment/(?P<sessionToken>[0-9a-z]+)', views.experiment, name='display_exp_info'),
    url(r'^tokens/(?P<token>[a-z0-9]+)/create', views.make_link_tokens, name='make_tokens'),
    url(r'^tokens/(?P<token>[a-z0-9]+)/view', views.group_token, name='token_status'),
    url(r'^config/$', views.new_config, name='new_config'),
    url(r'^config/(?P<sessionToken>[a-z0-9]+)$', views.show_config, name='display_config'),
    url(r'^config/(?P<sessionToken>[a-z0-9]+)/edit$', views.edit_config, name='edit_config'),
    url(r'^config/(?P<sessionToken>[a-z0-9]+)/new$', views.new_config, name='new_config'),
    url(r'^config/(?P<sessionToken>[a-z0-9]+)/copy$', views.copy_config, name='copy_config'),
    url(r'^data/(?P<sessionToken>[0-9a-z]+)$', views.show_data, name='display_data'),
    url(r'^data/(?P<sessionToken>[0-9a-z]+)/(?P<pkid>[0-9]+)$', views.show_data, name='display_data'),
    url(r'^data/(?P<sessionToken>[0-9a-z]+)/(?P<pkid>[0-9]+)/file$', views.one_data_file, name='one_data_file'),
    url(r'^data/(?P<sessionToken>[0-9a-z]+)/exp$', views.exp_data, name='display_exp_data'),
    url(r'^data/(?P<sessionToken>[0-9a-z]+)/exp/file$', views.download_data, name='download'),
    url(r'^status/(?P<sessionToken>[0-9a-z]+)$', views.return_status, name='show_status'),
    url(r'^study/$', views.studies, name='study_index'),
    url(r'^study/(?P<studyNumber>[0-9a-z]+)$', views.studies, name='study_index'),
    url(r'^security/', views.security_list, name='security_list'),
]

