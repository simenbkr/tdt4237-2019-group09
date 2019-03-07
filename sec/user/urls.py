from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path(r'^verify/(?P<token>[0-9a-f]+)/(?P<username>*)/', views.VerifyUser.as_view(), name='verify')
]
