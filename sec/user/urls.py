from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    re_path(r'^verify/(?P<token>[0-9a-f]+)/(?P<username>[\w.@+-]+)/?$', views.VerifyUser.as_view(), name='verify'),
    #path('forgot/, ')
]
