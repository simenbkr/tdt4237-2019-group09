from django.contrib.auth import login
from django.contrib.sessions.backends.cache import SessionStore
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView
from django.core.mail import EmailMessage
from .forms import SignUpForm, LoginForm, ForgotForm, EmailForm, ResetForm
from os import urandom
from binascii import hexlify
from django.contrib.auth.models import User
from django.views import View
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.shortcuts import render, redirect
from django.contrib import messages
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
            if user is not None and not user.profile.tmp_login:
                login(self.request, user)
                return super().form_valid(form)
        except:
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

        if user is not None and token == user.profile.token and len(user.profile.token) > 10:
            user.is_active = True
            user.save()
            user.profile.token = ''
            user.profile.save()

            messages.warning(request, "Your email was successfully verified. Please login.")
            return HttpResponseRedirect(reverse_lazy("home"))

        messages.warning(request, "Your e-mail could not be verified. Please try again.")
        return HttpResponseRedirect(reverse_lazy("home"))


class ForgotPassordEmail(FormView):
    form_class = EmailForm
    template_name = "user/enter_email.html"

    def form_valid(self, form):
        profile = Profile.objects.get(email=form.cleaned_data.get("email"))
        if profile is not None:
            return redirect('{}'.format(profile.email))

        form.add_error("No user with that email.")
        super().form_invalid(form)

    def form_invalid(self, form):
        form.add_error("Invalid email!")
        return super().form_invalid(form)


class ForgotPassword(FormView):
    form_class = ForgotForm
    template_name = "user/forgot_password.html"

    def form_valid(self, form):
        email = self.kwargs['email']
        profile = Profile.objects.get(email=email)
        user = profile.user
        sec_q = SecurityQuestionUser.objects.get(user=profile.user)

        if sec_q.security_question == form.cleaned_data.get('security_questions') and sec_q.answer == form.cleaned_data['answer']:
            tmp_pw = hexlify(urandom(32)).decode("utf-8")

            profile.tmp_login = True
            profile.token = hexlify(urandom(32)).decode("utf-8")
            profile.save()

            user.set_password(tmp_pw)
            user.save()

            email_subject = "[TDT4237] [GR9] Password reset in progress."
            link = "http://{}/user/forgot/{}/{}".format(Site.objects.get_current().domain, profile.email, profile.token)
            email_content = "Link: {}\nPassword: {}".format(link, tmp_pw)
            email = EmailMessage(email_subject, email_content, from_email='NO REPLY <noreply@gr9progsexy.ntnu.no>',
                             to=[profile.email], reply_to=['noreply@gr9progsexy.ntnu.no'])

            email.send()

            messages.success("Your temporary password, with a link to login has been sent to your email")
            return HttpResponseRedirect(reverse_lazy('home'))

        messages.warning(self.request, "Something went wrong.. Please try again.")
        return HttpResponseRedirect(reverse_lazy('home'))


class ResetPassword(FormView):
    form_class = ResetForm
    template_name = "user/reset.html"

    def get(self, request, *args, **kwargs):
        profile = Profile.objects.get(email=kwargs['email'])
        if kwargs['token'] != profile.token:
            messages.warning(request, "Disallowed action! You do not have the correct token.")
            return HttpResponseRedirect(reverse_lazy('home'))

        else:
            return render(request, "user/reset.html", {'form': ResetForm})


    def form_valid(self, form):
        email = self.kwargs['email']
        token = self.kwargs['token']

        profile = Profile.objects.get(email=email)
        user = profile.user

        if token == profile.token and user.check_password(form.cleaned_data.get('temporary_pw')) and \
                form.cleaned_data.get('new_password1') == form.cleaned_data.get('new_password2'):

            user.set_password(form.cleaned_data.get('new_password1'))
            user.save()

            profile.tmp_login = False
            profile.token = ''
            profile.save()

            messages.success(self.request, "Password changed successfully.")
            return HttpResponseRedirect(reverse_lazy('home'))

        messages.warning(self.request, "Something went wrong.. Please try again.")
        return HttpResponseRedirect(reverse_lazy('home'))