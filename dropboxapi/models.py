from django.db import models
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class DropboxAccessTokens(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True)
    token = models.TextField()
    refresh_token = models.CharField(max_length=500, blank=True, null=True)
    token_type = models.CharField(max_length=50, default='Bearer')
    expires_in = models.DecimalField(null=True, decimal_places=0, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return f"{self.token}"

    def is_expired(self):
        print(self.created_at)
        if self.created_at is None:
            return True
        return self.created_at + timedelta(seconds=int(self.expires_in)) < timezone.now()

class DropboxReceipt(models.Model):
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expense = models.ForeignKey('expenses.Expense', related_name='dropbox_receipts', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.file_name}"
