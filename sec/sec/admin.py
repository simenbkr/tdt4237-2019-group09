from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.forms import ValidationError
from datetime import datetime, timedelta
from django.shortcuts import render
from django.conf import settings
from ..user.models import AccessAttempt, get_client_ip
from django.contrib import admin



class CustomAdminLoginForm(AuthenticationForm):

    def clean(self):

        ip = get_client_ip(self.request)
        newer_than = datetime.now() - timedelta(settings.COOLDOWN_TIME)
        count = len(list(AccessAttempt.objects.filter(attempt_time__gt=newer_than).filter(ip_addr=ip)))
        if count > 3:
            return render(self.request,
                          '{}/sec/templates/failed_login.html'.format(settings.BASE_DIR),
                          {'failure_limit': count})

        user = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if user and password:
            self.user_cache = authenticate(
                username=user,
                password=password
            )

            if self.user_cache is None:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class CustomAdminLoginSite(admin.AdminSite):
    site_header = 'Login'
    site_title = 'Login'
    index_title = 'Custom Admin Login'
    login_form = CustomAdminLoginForm


admin_site = CustomAdminLoginSite()