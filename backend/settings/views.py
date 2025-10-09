from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import UserPreferences
from .serializers import UserPreferencesSerializer, UserPreferencesUpdateSerializer


class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating user preferences.
    """
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Get or create user preferences for the current user."""
        preferences, created = UserPreferences.objects.get_or_create(
            user=self.request.user,
            defaults={
                'email_notifications': True,
                'push_notifications': True,
                'irrigation_reminders': True,
                'weather_alerts': True,
                'temperature_unit': 'celsius',
                'volume_unit': 'liters',
                'time_format': '24h',
                'default_irrigation_duration': 30,
                'default_irrigation_method': 'drip',
                'dashboard_refresh_interval': 300,
                'items_per_page': 10
            }
        )
        return preferences

    def get_serializer_class(self):
        """Use different serializer for updates."""
        if self.request.method in ['PUT', 'PATCH']:
            return UserPreferencesUpdateSerializer
        return UserPreferencesSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_preferences(request):
    """
    Reset user preferences to defaults.
    """
    try:
        preferences = get_object_or_404(UserPreferences, user=request.user)

        # Reset to defaults
        preferences.email_notifications = True
        preferences.push_notifications = True
        preferences.irrigation_reminders = True
        preferences.weather_alerts = True
        preferences.temperature_unit = 'celsius'
        preferences.volume_unit = 'liters'
        preferences.time_format = '24h'
        preferences.default_irrigation_duration = 30
        preferences.default_irrigation_method = 'drip'
        preferences.dashboard_refresh_interval = 300
        preferences.items_per_page = 10

        preferences.save()

        serializer = UserPreferencesSerializer(preferences)
        return Response(serializer.data)

    except Exception as e:
        return Response(
            {'error': f'Failed to reset preferences: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
