from rest_framework import serializers
from .models import WeatherData, WeatherForecast, WeatherAlert


class WeatherDataSerializer(serializers.ModelSerializer):
    """
    Serializer for current weather data.
    """
    wind_direction_cardinal = serializers.SerializerMethodField()

    class Meta:
        model = WeatherData
        fields = [
            'id', 'latitude', 'longitude', 'location_name',
            'temperature', 'feels_like', 'humidity', 'pressure',
            'wind_speed', 'wind_direction', 'wind_direction_cardinal',
            'weather_condition', 'weather_description', 'weather_icon',
            'rainfall_1h', 'rainfall_3h',
            'data_source', 'updated_at', 'is_stale'
        ]
        read_only_fields = ['id', 'updated_at', 'is_stale', 'wind_direction_cardinal']

    def get_wind_direction_cardinal(self, obj):
        return obj.get_wind_direction_cardinal()


class WeatherForecastSerializer(serializers.ModelSerializer):
    """
    Serializer for weather forecast data.
    """

    class Meta:
        model = WeatherForecast
        fields = [
            'id', 'latitude', 'longitude', 'location_name',
            'forecast_date', 'forecast_time',
            'temperature_min', 'temperature_max', 'humidity', 'pressure',
            'wind_speed', 'wind_direction', 'weather_condition',
            'weather_description', 'weather_icon',
            'precipitation_probability', 'rainfall_amount',
            'data_source', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']


class WeatherAlertSerializer(serializers.ModelSerializer):
    """
    Serializer for weather alerts.
    """
    duration_hours = serializers.SerializerMethodField()

    class Meta:
        model = WeatherAlert
        fields = [
            'id', 'latitude', 'longitude', 'location_name',
            'alert_type', 'severity', 'title', 'description',
            'start_time', 'end_time', 'duration_hours',
            'is_active', 'is_expired', 'data_source', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at', 'is_expired', 'duration_hours']

    def get_duration_hours(self, obj):
        return obj.duration_hours


class WeatherDataCreateSerializer(serializers.Serializer):
    """
    Serializer for creating weather data via API.
    Used when fetching weather data for specific coordinates.
    """
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=-90,
        max_value=90
    )
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=-180,
        max_value=180
    )
    location_name = serializers.CharField(max_length=255, required=False)


class WeatherForecastCreateSerializer(serializers.Serializer):
    """
    Serializer for requesting forecast data.
    """
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=-90,
        max_value=90
    )
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=-180,
        max_value=180
    )
    days = serializers.IntegerField(
        min_value=1,
        max_value=7,
        default=5,
        required=False
    )