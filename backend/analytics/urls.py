from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('stats/', views.water_usage_stats, name='water-usage-stats'),
    path('field/<int:field_id>/', views.field_analytics, name='field-analytics'),
    path('efficiency/', views.irrigation_efficiency_report, name='efficiency-report'),
]