from django.conf.urls.static import static
#from django.contrib import admin
from django.urls import include, path
from sec.admin import admin_site

from sec import settings

urlpatterns = [
    path('', include('home.urls')),
    path('admin/', include(admin_site.urls)),
    path('user/', include('user.urls')),
    path('projects/', include('projects.urls')),
    path('payment/', include('payment.urls')),
]