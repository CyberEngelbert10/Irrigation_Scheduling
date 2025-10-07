from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FieldViewSet

# Create router and register viewset
router = DefaultRouter()
router.register(r'', FieldViewSet, basename='field')

urlpatterns = [
    path('', include(router.urls)),
]
