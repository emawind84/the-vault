
from django.conf.urls import url

from . import views

urlpatterns = [
    # home page
    url(r'^$', views.index, name='index'),

    # show all topics
    url(r'^secrets/$', views.secrets, name='secrets'),

    # detail page for a single topic
    url(r'^secrets/(?P<secret_id>\d+)/$', views.secret, name='secret'),

    # page for adding a new topic
    url(r'^new_secret/$', views.new_secret, name='new_secret'),

    url(r'^edit_secret/(?P<secret_id>\d+)/$', views.edit_secret, name='edit_secret'),

    url(r'^delete_secret/(?P<secret_id>\d+)/$', views.delete_secret, name='delete_secret'),
]
