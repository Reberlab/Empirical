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
