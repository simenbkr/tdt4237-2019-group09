from django.contrib.auth import login
from django.contrib.sessions.backends.cache import SessionStore
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView
from django.core.mail import EmailMessage
from .forms import SignUpForm, LoginForm, ForgotForm, EmailForm
from os import urandom
from binascii import hexlify
from django.contrib.auth.models import User
from django.views import View
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.shortcuts import render, redirect
import logging
from .models import Profile, SecurityQuestion, SecurityQuestionUser

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

        sec_question = form.cleaned_data.get('security_questions')
        sec_q_user = SecurityQuestionUser.objects.create(user=user, security_question=sec_question,
                                                         answer=form.cleaned_data.get('answer'))
        sec_q_user.save()

        email_subject  = "[TDT4237] [GR9] Activate your user account."
        current_site = Site.objects.get_current()

        email_content = render_to_string('user/email_template.html', {'user': user, 'domain': current_site.domain,
                                                                      'token': user.profile.token})

        email = EmailMessage(email_subject, email_content, from_email='NO REPLY <noreply@gr9progsexy.ntnu.no>',
                             to=[user.profile.email], reply_to=['noreply@gr9progsexy.ntnu.no'])

        email.send()
        return render(self.request, self.success_url)


class VerifyUser(View):

    def get(self, request, token, username):
        user = User.objects.get(username=username)
        from django.contrib import messages

        if user is not None and token == user.profile.token and len(user.profile.token) > 10:
            user.is_active = True
            user.save()
            user.profile.token = ''
            user.profile.save()

            messages.warning(request, "Your email was successfully verified. Please login.")
            return HttpResponseRedirect(reverse_lazy("home"))

        messages.warning("Your e-mail could not be verified. Please try again.")
        return HttpResponseRedirect(reverse_lazy("home"))


class ForgotPassordEmail(FormView):
    form_class = EmailForm
    template_name = "user/enter_email.html"

    def form_valid(self, form):
        profile = Profile.objects.get(email=form.cleaned_data.get("email"))
        if profile is not None:
            return redirect('{}'.format(profile.email))

        return HttpResponse("No user with that email. Sorry bruh.")

    def form_invalid(self, form):
        return HttpResponse("u sux")


class ForgotPassword(FormView):
    form_class = ForgotForm
    template_name = "user/forgot_password.html"

    def form_valid(self, form):
        email = self.kwargs['email']
        profile = Profile.objects.get(email=email)
        user = profile.user
        sec_q = SecurityQuestionUser.objects.get(user=profile.user)

        if sec_q.security_question == form.cleaned_data.get('security_questions') and sec_q.answer == form.cleaned_data['answer']:
            tmp_pw = hexlify(urandom(16)).decode("utf-8")
            profile.tmp_login = True
            profile.save()
            user.set_password(tmp_pw)
            user.save()


            return HttpResponse("Your temporary password: {}".format(tmp_pw))

        return HttpResponse("Fuck off")


