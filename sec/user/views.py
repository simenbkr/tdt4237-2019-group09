from django.contrib.auth import login
from django.contrib.sessions.backends.cache import SessionStore
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView
from django.core.mail import EmailMessage
from .forms import SignUpForm, LoginForm
from os import urandom
from binascii import hexlify
from django.contrib.auth.models import User
from django.views import View
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.shortcuts import render, redirect
import logging

logger = logging.getLogger(__name__)

class IndexView(TemplateView):
    template_name = "sec/base.html"


def logout(request):
    request.session = SessionStore()
    return HttpResponseRedirect(reverse_lazy("home"))


class LoginView(FormView):
    form_class = LoginForm
    template_name = "user/login.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        try:
            from django.contrib.auth import authenticate
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(self.request, user)
                return super().form_valid(form)
        except e:
            pass

        ip = self.request.META.get('REMOTE_ADDR')
        logger.warning('invalid log-in attempt for user: {} from {}'.format(form.cleaned_data['username'], ip))
        form.add_error(None, "Provide a valid username and/or password")
        return super().form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)



class SignupView(CreateView):
    form_class = SignUpForm
    template_name = "user/signup.html"
    success_url = "user/email_sent.html"

    def form_valid(self, form):
        user = form.save()
        user.profile.company = form.cleaned_data.get("company")
        user.profile.categories.add(*form.cleaned_data["categories"])
        user.profile.email = form.cleaned_data.get("email")
        user.is_active = False
        user.profile.token = hexlify(urandom(32)).decode("utf-8")
        user.save()

        email_subject  = "[TDT4237] [GR9] Activate your user account."
        current_site = Site.objects.get_current()

        email_content = render_to_string('user/email_template.html', {'user': user, 'domain': current_site.domain, 'token': user.profile.token})

        email = EmailMessage(email_subject, email_content, from_email='NO REPLY <noreply@gr9progsexy.ntnu.no>',
                             to=[user.profile.email], reply_to=['noreply@gr9progsexy.ntnu.no'])

        email.send()
        return render(self.request, self.success_url)


class VerifyUser(View):

    def get(self, request, token, username):
        user = User.objects.get(username=username)
        from django.contrib import messages

        if user is not None and token == user.profile.token:
            user.is_active = True
            user.save()


            messages.warning(request, "Your email was successfully verified. Please login.")
            return HttpResponseRedirect(reverse_lazy("home"))

        messages.warning("Your e-mail could not be verified. Please try again.")
        return HttpResponseRedirect(reverse_lazy("home"))


class ForgotPassword(View):

    pass