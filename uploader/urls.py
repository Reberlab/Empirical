__author__ = 'drlemur'

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.index,name='uploader_index'),
    url(r'^review/$',views.unpack_review,name='uploader_review'),
    url(r'^error/',views.uploader_error,name='uploader_error'),
]

