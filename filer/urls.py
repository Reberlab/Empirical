from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.filer_index,name='filer_index'),
    url(r'^add/$',views.filer_add,name='filer_add'),
    url(r'^crypt/',views.filer_encrypt,name='filer_encrypt'),
    url(r'^filer/',views.filer_serve,name='filer_serve'),
    url(r'^edit/',views.filer_manage,name='filer_manage'),
]