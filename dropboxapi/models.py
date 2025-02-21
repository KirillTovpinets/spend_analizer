from django.db import models

# Create your models here.
class DropboxAccessTokens(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True)
    token = models.TextField()
    refresh_token = models.CharField(max_length=500, blank=True, null=True)
    token_type = models.CharField(max_length=50, default='Bearer')
    expires_in = models.DecimalField(null=True, decimal_places=0, max_digits=10)

    def __str__(self):
        return f"{self.token}"

