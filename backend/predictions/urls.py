from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IrrigationScheduleViewSet,
    IrrigationHistoryViewSet,
    PredictionViewSet
)

# Create a router for the API
router = DefaultRouter()
router.register(r'schedules', IrrigationScheduleViewSet, basename='irrigation-schedule')
router.register(r'history', IrrigationHistoryViewSet, basename='irrigation-history')
router.register(r'predict', PredictionViewSet, basename='prediction')

urlpatterns = [
    path('', include(router.urls)),
]