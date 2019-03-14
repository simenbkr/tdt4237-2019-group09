from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.db.models.signals import post_save
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from datetime import datetime, timedelta
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tmp_login = models.BooleanField(default=False)
    email = models.EmailField(max_length=100, blank=True, unique=True)
    token = models.CharField(max_length=128, blank=True, null=True)
    company = models.TextField(max_length=50, blank=True)
    phone_number = models.TextField(max_length=50, blank=True)
    street_address = models.TextField(max_length=50, blank=True)
    city = models.TextField(max_length=50, blank=True)
    state = models.TextField(max_length=50, blank=True)
    postal_code = models.TextField(max_length=50, blank=True)
    country = models.TextField(max_length=50, blank=True)
    categories = models.ManyToManyField('projects.ProjectCategory', related_name='competance_categories')
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, blank=True, default=None, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


@receiver(user_logged_in)
def update_session(sender, request, **kwargs):
    if request.user.profile.session is not None:
        request.session = SessionStore(session_key=request.user.profile.session.session_key)
        request.session.modified = True
    else:
        request.user.profile.session_id = request.session.session_key
        request.user.profile.save()


class SecurityQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=200, null=False)

    def __str__(self):
        return self.question


class SecurityQuestionUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    security_question = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200, null=False)

    def __str__(self):
        return "{}: {}".format(self.user.username, self.security_question.question)


def get_client_ip(request):
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        ip = x_real_ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AccessAttempt(models.Model):
    user_agent = models.CharField(max_length=255, blank=True)
    ip_addr = models.GenericIPAddressField()
    username = models.CharField(max_length=255)
    attempt_time = models.DateTimeField()
    login_valid = models.BooleanField()


def allowed_to_login(request):
    """
    After LOCKOUT_COUNT attempts in the last COOLDOWN_TIME hours, the client behind the requests IP is no longer
    allowed to attempt logins.
    """

    ip = get_client_ip(request)
    newer_than = datetime.now() - timedelta(settings.COOLDOWN_TIME)
    count = len(list(AccessAttempt.objects.filter(attempt_time__gt=newer_than).filter(ip_addr=ip)))

    return count < settings.LOCKOUT_COUNT


@receiver(user_login_failed)
def handle_failed_login(sender, credentials, request, **kwargs):
    """
    Log the information belonging to the client attempting to log in.
    """

    ip = get_client_ip(request)

    a = AccessAttempt()
    a.user_agent = request.META['HTTP_USER_AGENT']
    a.ip_addr = ip
    a.attempt_time = datetime.now()
    a.login_valid = 0
    a.username = credentials['username']
    a.save()


@receiver(user_logged_in)
def handle_logged_in(sender, request, **kwargs):
    """
    Reset the attempts made by this client on this user and ip touple.
    """
    ip = get_client_ip(request)
    # AccessAttempt.objects.filter(ip_addr=ip).filter(username=credentials['username']).delete()
    AccessAttempt.objects.filter(ip_addr=ip).delete()
