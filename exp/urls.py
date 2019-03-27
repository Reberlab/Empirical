__author__ = 'Paul J. Reber'

from django.urls import path
from . import views

urlpatterns = [
    # UI urls for web interface:
    path('',views.index),
    path('study/',views.index,name='study_index'),
    path('study/new',views.edit_study,name='edit_study'),
    path('study/<int:studyNumber>/edit',views.edit_study,name='edit_study'),
    path('study/<int:studyNumber>',views.one_study,name='one_study'),
    path('experiment/<int:expNumber>/edit',views.edit_experiment,name='edit_experiment'),
    path('experiment/<int:studyNumber>/new',views.edit_experiment,name='new_experiment'), # note -- will have different passed values, new exp
    path('experiment/<int:expNumber>',views.one_experiment,name='one_experiment'),
    path('config/',views.new_config,name='new_config'),
    path('config/<str:sessionToken>/edit',views.edit_config,name='edit_config'),
    path('config/<str:sessionToken>/copy', views.copy_config,name='copy_config'),
    path('config/<str:sessionToken>',views.one_session,name='one_session'),
    path('config/<int:expNumber>/new',views.new_config,name='new_config'),
    path('data/exp/<int:expNumber>',views.experiment_data,name='experiment_data'),
    path('data/session/<str:sessionToken>/<int:pkid>',views.session_data,name='session_data'),
    path('data/session/<str:sessionToken>',views.session_data,name='session_data'),
    path('data/file/exp/<int:expNumber>',views.download_exp_data,name='download_experiment'),
    path('data/file/exp/<int:expNumber>/type/<str:reportType>', views.download_exp_data,name='download_exp_type'),
    path('data/file/exp/<int:expNumber>/since/<int:since>', views.download_exp_data,name='download_exp_since'),
    path('data/file/session/<str:sessionToken>',views.download_session_data,name='download_session'),
    path('data/file/session/<str:sessionToken>/<int:pkid>',views.download_session_data,name='download_session'),
    path('participants/',views.participant_table,name='participant_table'),
    path('participants/<str:name>', views.one_participant, name='one_participant'),
    path('updateparticipants/', views.participants_update, name='participant_update'),
    path('security/',views.security_list,name='security_list'),

    # App urls for running experiments to communicate with server
    path('start/<str:groupToken>/<str:workerId>', views.start_session),
    path('start/<str:groupToken>/',views.start_session),
    path('newstart/<str:groupToken>/<str:workerId>',views.newstart_session),
    path('report/<str:sessionToken>',views.report),
    path('status/<str:sessionToken>/<str:workerId>',views.return_status),
    path('status/<str:sessionToken>/', views.return_status),
]

    # Django 1.x
    # url(r'^$',views.index,name='study_index'),
    # url(r'^study/(?P<studyNumber>[0-9a-z]+)$', views.one_study, name='one_study'),
    # url(r'^study/$', views.edit_study, name='edit_study'),
    # url(r'^study/(?P<studyNumber>[0-9a-z]+)/edit$', views.edit_study, name='edit_study'),
    # url(r'^experiment/(?P<expNumber>[0-9a-z]+)$', views.one_experiment, name='one_experiment'),
    # url(r'^experiment/(?P<studyNumber>[0-9a-z]+)/new$', views.edit_experiment, name='new_experiment'),
    # url(r'^experiment/(?P<expNumber>[0-9a-z]+)/edit$', views.edit_experiment, name='edit_experiment'),
    # url(r'^config/$', views.new_config, name='new_config'),
    # url(r'^config/(?P<sessionToken>[a-z0-9]+)$', views.one_session, name='one_session'),
    # url(r'^config/(?P<sessionToken>[a-z0-9]+)/edit$', views.edit_config, name='edit_config'),
    # url(r'^config/(?P<expNumber>[a-z0-9]+)/new$', views.new_config, name='new_config'),
    # url(r'^config/(?P<sessionToken>[a-z0-9]+)/copy$', views.copy_config, name='copy_config'),
    #
    # url(r'^data/(?P<studyId>[0-9a-z]+)$',views.study_data,name='study_data'),
    # url(r'^data/exp/(?P<expId>[0-9a-z]+)$', views.experiment_data, name='experiment_data'),
    # url(r'^data/session/(?P<sessionToken>[0-9a-z]+)$', views.session_data, name='session_data'),
    # url(r'^data/session/(?P<sessionToken>[0-9a-z]+)/(?P<pkid>[0-9a-z]+)$', views.session_data, name='session_data'),
    # url(r'^data/file/exp/(?P<expId>[0-9a-z]+)$', views.download_exp_data, name='download_experiment'),
    # url(r'^data/file/exp/(?P<expId>[0-9a-z]+)/(?P<reportType>[0-9a-z]+)$', views.download_exp_data, name='download_experiment'),
    # url(r'^data/file/session/(?P<sessionToken>[0-9a-z]+)$', views.download_session_data, name='download_session'),
    # url(r'^data/file/session/(?P<sessionToken>[0-9a-z]+)/(?P<pkid>[0-9a-z]+)$', views.download_session_data, name='download_session'),
    #
    # url(r'^security/', views.security_list, name='security_list'),
    # # the app urls:
    # url(r'^start/(?P<groupToken>[0-9a-z]+)/(?P<workerId>[0-9a-zA-Z_]+)$', views.start_session, name='start_session'),
    # url(r'^start/(?P<groupToken>[0-9a-z]+)$', views.start_session, name='start_session'),
    # url(r'^newstart/(?P<groupToken>[0-9a-z]+)/(?P<workerId>[0-9a-zA-Z_]+)$', views.newstart_session, name='newstart_session'),
    # url(r'^report/(?P<sessionToken>[0-9a-z]+)', views.report, name='report_exp'),
    # url(r'^status/(?P<sessionToken>[0-9a-z]+)$', views.return_status, name='show_status'),
    # url(r'^status/(?P<sessionToken>[0-9a-z]+)/(?P<workerId>[0-9a-zA-Z_]+)$', views.return_status, name='show_status'),


