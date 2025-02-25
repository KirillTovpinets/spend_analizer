from django.contrib import admin
from .models import Receipt, Expense, ExpenseItem
from dropboxapi.models import DropboxReceipt
# Register your models here.
@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['image', 'uploaded_at', 'expense']
    list_filter = ['image', 'uploaded_at']
    search_fields = ['uploaded_at']


class ReceptInline(admin.TabularInline):
    model = Receipt
    extra = 0

class DropboxReceiptInline(admin.TabularInline):
    model = DropboxReceipt
    extra = 0


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['merchant', 'category', 'amount', 'transaction_date']
    list_filter = ['category', 'created_at']
    search_fields = ['category', 'description', 'merchant', 'amount']
    inlines = [ReceptInline, DropboxReceiptInline]


@admin.register(ExpenseItem)
class ExpenseItemAdmin(admin.ModelAdmin):
    list_display = ['expense', 'description', 'price', 'total']
    list_filter = ['expense', 'description']
    search_fields = ['description']
