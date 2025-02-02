from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.exceptions import PermissionDenied

ALLOWED_EMAILS = ['kirill8']

@receiver(user_logged_in)
def check_user_email(sender, request, user, **kwargs):
    print(user)
    if user not in ALLOWED_EMAILS:
        raise PermissionDenied("Your account is not authorized.")
    return user
