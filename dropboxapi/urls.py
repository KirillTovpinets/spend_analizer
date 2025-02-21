# urls.py
from django.urls import path
from . import views

app_name = 'dropboxapi'

urlpatterns = [
    path('login/', views.dropbox_login, name='dropbox_login'),
    path('dropbox-callback/', views.dropbox_callback, name='dropbox_callback'),
    path('files/', views.list_files, name='dropbox_files'),
]

