from django.contrib import admin
from django.urls import include, path

from service.panel.views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),

    # REST API
    path('api/services/', include('service.api.urls')),

    # HTML management panel
    path('services/', include('service.panel.urls')),
]
