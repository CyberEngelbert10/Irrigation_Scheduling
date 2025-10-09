from rest_framework import serializers
from .models import UserPreferences


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user preferences."""

    class Meta:
        model = UserPreferences
        fields = [
            'id',
            'user',
            'email_notifications',
            'push_notifications',
            'irrigation_reminders',
            'weather_alerts',
            'temperature_unit',
            'volume_unit',
            'time_format',
            'default_irrigation_duration',
            'default_irrigation_method',
            'dashboard_refresh_interval',
            'items_per_page',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UserPreferencesUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user preferences."""

    class Meta:
        model = UserPreferences
        fields = [
            'email_notifications',
            'push_notifications',
            'irrigation_reminders',
            'weather_alerts',
            'temperature_unit',
            'volume_unit',
            'time_format',
            'default_irrigation_duration',
            'default_irrigation_method',
            'dashboard_refresh_interval',
            'items_per_page'
        ]