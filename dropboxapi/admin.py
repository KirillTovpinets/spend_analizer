from django.contrib import admin
from .models import DropboxAccessTokens
# Register your models here.
@admin.register(DropboxAccessTokens)
class DropboxAccessTokensAdmin(admin.ModelAdmin):
    list_display = ['token']
    list_filter = ['token']
    search_fields = ['token']
