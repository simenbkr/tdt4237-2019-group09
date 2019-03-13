from django.db import models
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from datetime import datetime


def get_client_ip(request):
    x_real_ip = request.META.get('X-Real-IP')
    if x_real_ip:
        ip = x_real_ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AccessAttempt(models):
    user_agent = models.CharField(max_length=255, blank=True)
    ip_addr = models.GenericIPAddressField()
    username = models.CharField(max_length=255)
    attempt_time = models.DateTimeField()
    login_valid = models.BooleanField()


@receiver(user_login_failed)
def hande_failed_login(sender, credentials, request, **kwargs):

    ip = get_client_ip(request)

    a = AccessAttempt()
    a.user_agent = request.META['HTTP_USER_AGENT']
    a.ip_addr = ip
    a.attempt_time = datetime.now()
    a.login_valid = 0
    a.username = credentials['username']
    a.save()

