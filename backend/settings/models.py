from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UserPreferences(models.Model):
    """
    User preferences and settings for customization.
    """

    # Temperature units
    TEMPERATURE_UNITS = [
        ('celsius', 'Celsius (°C)'),
        ('fahrenheit', 'Fahrenheit (°F)'),
    ]

    # Volume units
    VOLUME_UNITS = [
        ('liters', 'Liters (L)'),
        ('gallons', 'Gallons (gal)'),
    ]

    # Time format
    TIME_FORMATS = [
        ('12h', '12-hour (AM/PM)'),
        ('24h', '24-hour'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences'
    )

    # Notification preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text='Receive email notifications for irrigation schedules'
    )
    push_notifications = models.BooleanField(
        default=True,
        help_text='Receive push notifications in the browser'
    )
    irrigation_reminders = models.BooleanField(
        default=True,
        help_text='Receive reminders for scheduled irrigation'
    )
    weather_alerts = models.BooleanField(
        default=True,
        help_text='Receive weather-related alerts'
    )

    # Unit preferences
    temperature_unit = models.CharField(
        max_length=20,
        choices=TEMPERATURE_UNITS,
        default='celsius',
        help_text='Preferred temperature unit'
    )
    volume_unit = models.CharField(
        max_length=20,
        choices=VOLUME_UNITS,
        default='liters',
        help_text='Preferred volume unit'
    )
    time_format = models.CharField(
        max_length=10,
        choices=TIME_FORMATS,
        default='24h',
        help_text='Preferred time format'
    )

    # Default irrigation settings
    default_irrigation_duration = models.PositiveIntegerField(
        default=30,
        help_text='Default irrigation duration in minutes'
    )
    default_irrigation_method = models.CharField(
        max_length=50,
        choices=[
            ('drip', 'Drip Irrigation'),
            ('sprinkler', 'Sprinkler System'),
            ('flood', 'Flood Irrigation'),
            ('manual', 'Manual Watering'),
        ],
        default='drip',
        help_text='Default irrigation method'
    )

    # UI preferences
    dashboard_refresh_interval = models.PositiveIntegerField(
        default=300,
        help_text='Dashboard auto-refresh interval in seconds (0 = disabled)'
    )
    items_per_page = models.PositiveIntegerField(
        default=10,
        help_text='Number of items to display per page in lists'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Preferences"
        verbose_name_plural = "User Preferences"

    def __str__(self):
        return f"{self.user.email}'s preferences"
