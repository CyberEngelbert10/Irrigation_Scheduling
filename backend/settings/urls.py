from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('preferences/', views.UserPreferencesView.as_view(), name='user-preferences'),
    path('preferences/reset/', views.reset_preferences, name='reset-preferences'),
]