from django.contrib import admin
from .models import DropboxAccessTokens, DropboxReceipt
# Register your models here.
@admin.register(DropboxAccessTokens)
class DropboxAccessTokensAdmin(admin.ModelAdmin):
    list_display = ['token']
    list_filter = ['token']
    search_fields = ['token']


@admin.register(DropboxReceipt)
class DropboxReceiptAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'expense', 'created_at']
    list_filter = ['file_name']
    search_fields = ['file_name']
