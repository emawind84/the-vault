"""Defines URL patterns for users"""

from django.conf.urls import url
from django.contrib.auth.views import login
from django.urls import path, reverse
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # login page
    url(r'^login/$', login, {'template_name': 'users/login.html'}, name='login'),

    # logout page
    url(r'^logout/$', views.logout_view, name='logout'),

    # registration page
    url(r'^register/$', views.register, name='register'),

    path('edit_user/', views.edit_user, name='edit_user'),

    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='users/change_password.html',), name='password_change'),

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='users/reset_password.html', 
        success_url='/users/password_reset/done/'), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/reset_password_done.html'), name='password_reset_done'),
]
