from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'weather-data', views.WeatherDataViewSet, basename='weather-data')
router.register(r'forecast', views.WeatherForecastViewSet, basename='forecast')
router.register(r'alerts', views.WeatherAlertViewSet, basename='alerts')

# URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),

    # Additional endpoints
    path('refresh/', views.refresh_weather_data, name='refresh-weather-data'),
    path('summary/', views.weather_summary, name='weather-summary'),
    path('stats/', views.WeatherStatsView.as_view(), name='weather-stats'),
]