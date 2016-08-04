__author__ = 'drlemur'

from django.conf.urls import url
from . import views

urlpatterns = [
    # UI urls:
    url(r'^$',views.index,name='study_index'),
    url(r'^study/(?P<studyNumber>[0-9a-z]+)$', views.one_study, name='one_study'),
    url(r'^study/$', views.edit_study, name='edit_study'),
    url(r'^study/(?P<studyNumber>[0-9a-z]+)/edit$', views.edit_study, name='edit_study'),
    url(r'^experiment/(?P<expNumber>[0-9a-z]+)$', views.one_experiment, name='one_experiment'),
    url(r'^experiment/(?P<studyNumber>[0-9a-z]+)/new$', views.edit_experiment, name='new_experiment'),
    url(r'^experiment/(?P<expNumber>[0-9a-z]+)/edit$', views.edit_experiment, name='edit_experiment'),
    url(r'^config/$', views.new_config, name='new_config'),
    url(r'^config/(?P<sessionToken>[a-z0-9]+)$', views.one_session, name='one_session'),
    url(r'^config/(?P<sessionToken>[a-z0-9]+)/edit$', views.edit_config, name='edit_config'),
    url(r'^config/(?P<expNumber>[a-z0-9]+)/new$', views.new_config, name='new_config'),
    url(r'^config/(?P<sessionToken>[a-z0-9]+)/copy$', views.copy_config, name='copy_config'),

    url(r'^data/(?P<studyId>[0-9a-z]+)$',views.study_data,name='study_data'),
    url(r'^data/exp/(?P<expId>[0-9a-z]+)$', views.experiment_data, name='experiment_data'),
    url(r'^data/session/(?P<sessionToken>[0-9a-z]+)$', views.session_data, name='session_data'),
    url(r'^data/session/(?P<sessionToken>[0-9a-z]+)/(?P<pkid>[0-9a-z]+)$', views.session_data, name='session_data'),
    url(r'^data/file/exp/(?P<expId>[0-9a-z]+)$', views.download_exp_data, name='download_experiment'),
    url(r'^data/file/exp/(?P<expId>[0-9a-z]+)/(?P<reportType>[0-9a-z]+)$', views.download_exp_data, name='download_experiment'),
    url(r'^data/file/session/(?P<sessionToken>[0-9a-z]+)$', views.download_session_data, name='download_session'),
    url(r'^data/file/session/(?P<sessionToken>[0-9a-z]+)/(?P<pkid>[0-9a-z]+)$', views.download_session_data, name='download_session'),
    #url(r'^data/(?P<sessionToken>[0-9a-z]+)$', views.show_data, name='display_data'),
    #url(r'^data/(?P<sessionToken>[0-9a-z]+)/(?P<pkid>[0-9]+)$', views.show_data, name='display_data'),
    #url(r'^data/(?P<sessionToken>[0-9a-z]+)/(?P<pkid>[0-9]+)/file$', views.one_data_file, name='one_data_file'),
    #url(r'^data/(?P<sessionToken>[0-9a-z]+)/exp$', views.exp_data, name='display_exp_data'),
    #url(r'^data/(?P<sessionToken>[0-9a-z]+)/exp/file$', views.download_data, name='download'),

    url(r'^security/', views.security_list, name='security_list'),
    # the app urls:
    #url(r'^group/(?P<groupToken>[0-9a-z]+)$', views.get_session, name='get_session'),
    #url(r'^group/(?P<groupToken>[0-9a-z]+)/(?P<workerId>[0-9a-zA-Z_]+)$', views.get_session, name='get_session'),
    #url(r'^start/(?P<sessionToken>[0-9a-z]+)$', views.start, name='start_exp'),
    #url(r'^start/(?P<sessionToken>[0-9a-z]+)/(?P<args>[0-9a-zA-Z]+)$', views.start, name='start_exp'),
    url(r'^start/(?P<groupToken>[0-9a-z]+)/(?P<workerId>[0-9a-zA-Z_]+)$', views.start_session, name='start_session'),
    url(r'^start/(?P<groupToken>[0-9a-z]+)$', views.start_session, name='start_session'),
    url(r'^newstart/(?P<groupToken>[0-9a-z]+)/(?P<workerId>[0-9a-zA-Z_]+)$', views.newstart_session, name='newstart_session'),
    #url(r'^consent/(?P<sessionToken>[0-9a-z]+)', views.get_consent, name='get_consent'),
    url(r'^report/(?P<sessionToken>[0-9a-z]+)', views.report, name='report_exp'),
    url(r'^status/(?P<sessionToken>[0-9a-z]+)$', views.return_status, name='show_status'),
    url(r'^status/(?P<sessionToken>[0-9a-z]+)/(?P<workerId>[0-9a-zA-Z_]+)$', views.return_status, name='show_status'),
]

