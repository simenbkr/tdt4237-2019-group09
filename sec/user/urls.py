from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    re_path(r'^verify/(?P<token>[0-9a-f]+)/(?P<username>[\w.@+-]+)/?$', views.VerifyUser.as_view(), name='verify'),
    path('forgot/', views.ForgotPasswordEmail.as_view(), name='email_form'),
    re_path(r'^forgot/(?P<email>.*@.*)/(?P<token>[0-9a-f]+)/?$', views.ResetPassword.as_view(), name='reset password'),
    re_path(r'^forgot/(?P<email>.*@.*)/?$', views.ForgotPassword.as_view(), name='security question form'),

]
