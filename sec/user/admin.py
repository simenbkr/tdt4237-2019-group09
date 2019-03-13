from django.contrib import admin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.forms import ValidationError
from .models import Profile, SecurityQuestion, SecurityQuestionUser
from datetime import datetime, timedelta
from ..user.models import AccessAttempt, get_client_ip
from django.shortcuts import render


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


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

    list_display = ('username', 'email', 'first_name', 'last_name', 'get_company', 'is_active')
    list_editable = ('is_active',)

    def get_company(self, obj):
        return obj.profile.company

    get_company.admin_order_field = 'company'
    get_company.short_description = 'Company'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class CustomAdminLoginSite(admin.AdminSite):
    site_header = 'Login'
    site_title = 'Login'
    index_title = 'Custom Admin Login'
    login_form = CustomAdminLoginForm


admin_site = CustomAdminLoginSite()

admin_site.unregister(User)                    # TODO: COMMENT OUT THIS LINE REF OTG-CONFIG-005
admin_site.register(User, CustomUserAdmin)
admin_site.register(SecurityQuestion)
admin_site.register(SecurityQuestionUser)
admin_site.register(Profile)                   # TODO: COMMENT OUT THIS LINE REF OTG-CONFIG-005
