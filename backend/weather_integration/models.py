from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


class WeatherData(models.Model):
    """
    Model to cache weather data from external APIs.
    Stores current weather conditions and forecasts.
    """

    # Location information
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Longitude coordinate"
    )
    location_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Human-readable location name (e.g., 'Lusaka, Zambia')"
    )

    # Weather data
    temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Temperature in Celsius"
    )
    feels_like = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Feels like temperature in Celsius"
    )
    humidity = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Humidity percentage (0-100)"
    )
    pressure = models.PositiveIntegerField(
        help_text="Atmospheric pressure in hPa"
    )
    wind_speed = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Wind speed in m/s"
    )
    wind_direction = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(360)],
        help_text="Wind direction in degrees (0-360)"
    )
    weather_condition = models.CharField(
        max_length=100,
        help_text="Weather condition (e.g., 'Clear', 'Rain', 'Clouds')"
    )
    weather_description = models.CharField(
        max_length=255,
        help_text="Detailed weather description"
    )
    weather_icon = models.CharField(
        max_length=10,
        help_text="Weather icon code from API"
    )

    # Precipitation data
    rainfall_1h = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Rainfall in last 1 hour (mm)"
    )
    rainfall_3h = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Rainfall in last 3 hours (mm)"
    )

    # Metadata
    data_source = models.CharField(
        max_length=50,
        default='openweathermap',
        help_text="Source of weather data (e.g., 'openweathermap')"
    )
    api_response = models.JSONField(
        help_text="Raw API response for debugging"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Weather Data"
        verbose_name_plural = "Weather Data"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['location_name']),
        ]

    def __str__(self):
        location = self.location_name or f"{self.latitude}, {self.longitude}"
        return f"{location} - {self.weather_condition} ({self.temperature}°C)"

    @property
    def is_stale(self):
        """
        Check if weather data is older than 30 minutes.
        Weather data should be refreshed periodically.
        """
        return timezone.now() - self.updated_at > timedelta(minutes=30)

    def get_wind_direction_cardinal(self):
        """
        Convert wind direction degrees to cardinal direction.
        """
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = round(self.wind_direction / 22.5) % 16
        return directions[index]


class WeatherForecast(models.Model):
    """
    Model to store weather forecast data (7-day forecast).
    """

    # Location (same as WeatherData)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    location_name = models.CharField(max_length=255, blank=True, null=True)

    # Forecast specific data
    forecast_date = models.DateField(help_text="Date of the forecast")
    forecast_time = models.TimeField(help_text="Time of the forecast")

    # Weather data (similar to WeatherData but for forecast)
    temperature_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Minimum temperature in Celsius"
    )
    temperature_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Maximum temperature in Celsius"
    )
    humidity = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    pressure = models.PositiveIntegerField()
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2)
    wind_direction = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(360)]
    )
    weather_condition = models.CharField(max_length=100)
    weather_description = models.CharField(max_length=255)
    weather_icon = models.CharField(max_length=10)

    # Precipitation probability and amount
    precipitation_probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Probability of precipitation (0-100%)"
    )
    rainfall_amount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Expected rainfall amount (mm)"
    )

    # Metadata
    data_source = models.CharField(max_length=50, default='openweathermap')
    api_response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Weather Forecast"
        verbose_name_plural = "Weather Forecasts"
        ordering = ['forecast_date', 'forecast_time']
        indexes = [
            models.Index(fields=['latitude', 'longitude', 'forecast_date']),
            models.Index(fields=['forecast_date']),
            models.Index(fields=['location_name']),
        ]
        unique_together = ['latitude', 'longitude', 'forecast_date', 'forecast_time']

    def __str__(self):
        location = self.location_name or f"{self.latitude}, {self.longitude}"
        return f"{location} - {self.forecast_date} {self.forecast_time}: {self.weather_condition}"


class WeatherAlert(models.Model):
    """
    Model to store weather alerts and warnings.
    """

    # Location
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    location_name = models.CharField(max_length=255, blank=True, null=True)

    # Alert information
    alert_type = models.CharField(
        max_length=100,
        help_text="Type of alert (e.g., 'Heavy Rain', 'Heat Wave', 'Storm')"
    )
    severity = models.CharField(
        max_length=50,
        choices=[
            ('minor', 'Minor'),
            ('moderate', 'Moderate'),
            ('severe', 'Severe'),
            ('extreme', 'Extreme'),
        ],
        default='moderate'
    )
    title = models.CharField(max_length=255, help_text="Alert title/headline")
    description = models.TextField(help_text="Detailed alert description")
    start_time = models.DateTimeField(help_text="When the alert starts")
    end_time = models.DateTimeField(help_text="When the alert ends")

    # Source information
    data_source = models.CharField(max_length=50, default='openweathermap')
    api_response = models.JSONField()

    # Status
    is_active = models.BooleanField(default=True, help_text="Whether alert is currently active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Weather Alert"
        verbose_name_plural = "Weather Alerts"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['is_active', 'end_time']),
            models.Index(fields=['severity']),
        ]

    def __str__(self):
        location = self.location_name or f"{self.latitude}, {self.longitude}"
        return f"{self.severity.upper()} {self.alert_type} - {location}"

    @property
    def is_expired(self):
        """Check if the alert has expired."""
        return timezone.now() > self.end_time

    @property
    def duration_hours(self):
        """Calculate alert duration in hours."""
        return (self.end_time - self.start_time).total_seconds() / 3600
