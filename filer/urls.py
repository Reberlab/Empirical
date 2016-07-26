from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.filer_index,name='filer_index'),
    url(r'^add/$',views.filer_add,name='filer_add'),
    url(r'^crypt/',views.filer_encrypt,name='filer_encrypt'),
    url(r'^filer/',views.filer_serve,name='filer_serve'),
    url(r'^edit/',views.filer_manage,name='filer_manage'),
    url(r'^cleanup/',views.filer_ziptmp,name='filer_cleanup'),
    url(r'^zip/',views.prep_upload,name='prep_upload'),
    url(r'^images/',views.upload_images,name='upload_images'),
    url(r'^sessions/(?P<studyNumber>[0-9a-z]+)$',views.upload_zip,name='upload_sessions'),
    url(r'^sessions/(?P<studyNumber>[0-9a-z]+)/(?P<expNumber>[0-9a-z]+)$', views.upload_zip, name='upload_into_exp')
]

# From old Uploader
#urlpatterns = [
#    url(r'^$',views.index,name='uploader_index'),
#    url(r'^review/$',views.unpack_review,name='uploader_review'),
#    url(r'^error/',views.uploader_error,name='uploader_error'),
#]

