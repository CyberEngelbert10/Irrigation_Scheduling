"""
Main URL configuration for irrigation scheduler project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/fields/', include('apps.fields.urls')),
    path('api/weather/', include('weather_integration.urls')),
]
