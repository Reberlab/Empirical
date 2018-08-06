from django.urls import path
from . import views

urlpatterns = [
    path('',views.filer_index,name='filer_index'),
    path('add/<str:filename>',views.filer_add,name='filer_add'),
    path('add/',views.filer_add,name='filer_add'),
    path('show/<str:filename>',views.filer_serve,name='filer_serve'),
    path('show/<str:filename>/<int:version>',views.filer_serve,name='filer_serve'),
    path('versions/<str:filename>',views.filer_versions,name='filer_versions'),
    path('versions/<str:filename>/<int:version>',views.filer_versions,name='filer_versions'),
    path('edit/',views.filer_manage,name='filer_manage'),
    path('cleanup/',views.filer_ziptmp,name='filer_cleanup'),
    path('zip/',views.prep_upload,name='prep_upload'),
    path('images/',views.upload_images,name='upload_images'),
    path('sessions/<int:studyNumber>/<int:expNumber>',views.upload_zip,name='upload_into_exp'),
    path('sessions/<int:studyNumber>',views.upload_zip,name='upload_sessions')
]

    # url(r'^$',views.filer_index,name='filer_index'),
    # url(r'^add/$',views.filer_add,name='filer_add'),
    # url(r'^crypt/',views.filer_encrypt,name='filer_encrypt'),
    # url(r'^filer/',views.filer_serve,name='filer_serve'),
    # url(r'^edit/',views.filer_manage,name='filer_manage'),
    # url(r'^cleanup/',views.filer_ziptmp,name='filer_cleanup'),
    # url(r'^zip/',views.prep_upload,name='prep_upload'),
    # url(r'^images/',views.upload_images,name='upload_images'),
    # url(r'^sessions/(?P<studyNumber>[0-9a-z]+)$',views.upload_zip,name='upload_sessions'),
    # url(r'^sessions/(?P<studyNumber>[0-9a-z]+)/(?P<expNumber>[0-9a-z]+)$', views.upload_zip, name='upload_into_exp')



