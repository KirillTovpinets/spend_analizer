# urls.py
from django.urls import path
from . import views

app_name = 'dropboxapi'

urlpatterns = [
    path('login/', views.dropbox_login, name='dropbox_login'),
    path('dropbox-callback/', views.dropbox_callback, name='dropbox_callback'),
    path('files/', views.list_files, name='dropbox_files'),
    path('remove-receipt/<int:receipt_id>/', views.remove_receipt, name='remove_receipt'),
    path('link-receipts/', views.link_receipt, name='link_receipt'),
]

