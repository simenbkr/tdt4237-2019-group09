import django
import sys
import platform
from time import time

from django.conf import settings
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import SuspiciousOperation
from django.utils.cache import patch_vary_headers
from django.contrib.sites.models import Site
from django.utils.http import http_date
from user.models import allowed_to_login, AccessAttempt
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.core.management import BaseCommand

class InformationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response


class SimpleSessionMiddleware(SessionMiddleware):

    def process_request(self, request):
        session_token = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        request.session = self.SessionStore(session_token)

    def process_response(self, request, response):
        domain = Site.objects.get_current().domain.split(':')[0]
        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            pass
        else:
            if empty:
                response.delete_cookie(
                    settings.SESSION_COOKIE_NAME,
                    path=settings.SESSION_COOKIE_PATH,
                    domain=domain,
                )
            if accessed:
                patch_vary_headers(response, ("Cookie",))
            if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty and response.status_code != 500:

                if settings.SESSION_EXPIRE_AT_BROWSER_CLOSE:
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires = http_date(time() + max_age)
                try:
                    request.session.save()
                except UpdateError:
                    raise SuspiciousOperation(
                        "The request's session was deleted before the "
                        "request completed. The user may have logged "
                        "out in a concurrent request, for example."
                    )
                response.set_cookie(
                    settings.SESSION_COOKIE_NAME,
                    request.session.session_key, max_age=max_age, expires=expires,
                    domain=domain,
                    path=settings.SESSION_COOKIE_PATH,
                    secure=settings.SESSION_COOKIE_SECURE,
                    httponly=settings.SESSION_COOKIE_HTTPONLY,
                )
        return response


class RestrictAdminPage(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response is None:
            return self.get_response(request)
        return response

    def process_request(self, request):

        if request.path.startswith(reverse('admin:login')):
            if not allowed_to_login(request):
                return render(request,
                              '{}/sec/templates/failed_login.html'.format(settings.BASE_DIR),
                              {'failure_limit': settings.LOCKOUT_COUNT})

        return None


class AccessCommand(BaseCommand):

    def handle(self, *args, **options):

        if options['reset']:
            objects = AccessAttempt.objects.all()
            num = len(list(objects))
            objects.delete()
            print("Deleted {} records.".format(num))

        elif options['list']:
            objects = AccessAttempt.objects.all()
            out = ''
            for object in objects:
                out += "{} | {} | {} | {} | {}".format(object.ip_addr, object.username, object.attempt_time,
                                                       object.user_agent, object.login_valid)

            print(out)

    def add_arguments(self, parser):

        parser.add_argument(
            '--reset',
            help='Reset the login attempts for all IPs'
        )

        parser.add_argument(
            '--list',
            help='List login attempts.'
        )
