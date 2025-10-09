from django.contrib import admin
from .models import UserPreferences


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """Admin interface for user preferences."""

    list_display = [
        'user',
        'email_notifications',
        'temperature_unit',
        'volume_unit',
        'default_irrigation_method',
        'updated_at'
    ]

    list_filter = [
        'email_notifications',
        'push_notifications',
        'temperature_unit',
        'volume_unit',
        'default_irrigation_method'
    ]

    search_fields = ['user__email', 'user__name']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notifications', {
            'fields': (
                'email_notifications',
                'push_notifications',
                'irrigation_reminders',
                'weather_alerts'
            )
        }),
        ('Units & Display', {
            'fields': (
                'temperature_unit',
                'volume_unit',
                'time_format'
            )
        }),
        ('Default Irrigation Settings', {
            'fields': (
                'default_irrigation_duration',
                'default_irrigation_method'
            )
        }),
        ('UI Preferences', {
            'fields': (
                'dashboard_refresh_interval',
                'items_per_page'
            )
        })
    )

    readonly_fields = ['created_at', 'updated_at']
