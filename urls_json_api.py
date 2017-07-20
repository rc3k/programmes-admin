from django.conf.urls import url

from .views import create_master_course, update_master_course, delete_master_course
from .views import create_scheduled_course, update_scheduled_course, delete_scheduled_course
from .views import create_group, update_group, delete_group

app_name = 'Programmes'
urlpatterns = [
    url(r'^create/master/$', create_master_course, name='create_master_course'),
    url(r'^update/master/$', update_master_course, name='update_master_course'),
    url(r'^delete/master/$', delete_master_course, name='delete_master_course'),
    url(r'^create/scheduled/$', create_scheduled_course, name='create_scheduled_course'),
    url(r'^update/scheduled/$', update_scheduled_course, name='update_scheduled_course'),
    url(r'^delete/scheduled/$', delete_scheduled_course, name='delete_scheduled_course'),
    url(r'^create/group/$', create_group, name='create_group'),
    url(r'^update/group/$', update_group, name='update_group'),
    url(r'^delete/group/$', delete_group, name='delete_group'),
]
