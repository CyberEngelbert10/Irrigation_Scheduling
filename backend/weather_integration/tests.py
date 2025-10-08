import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import WeatherData, WeatherForecast, WeatherAlert
from .services import OpenWeatherMapService, WeatherService
from .serializers import WeatherDataSerializer, WeatherForecastSerializer


class WeatherDataModelTest(TestCase):
    """
    Test cases for WeatherData model.
    """

    def setUp(self):
        self.weather_data = WeatherData.objects.create(
            latitude=Decimal('-15.3875'),
            longitude=Decimal('28.3228'),
            location_name='Lusaka, Zambia',
            temperature=Decimal('25.5'),
            feels_like=Decimal('27.0'),  # Required field
            humidity=65,
            pressure=1013,  # Required field
            wind_speed=Decimal('3.5'),  # Required field
            wind_direction=180,
            weather_condition='Clear',
            weather_description='clear sky',
            weather_icon='01d',
            rainfall_1h=Decimal('0.0'),
            rainfall_3h=Decimal('0.0'),
            data_source='openweathermap',
            api_response={'test': 'data'}
        )

    def test_weather_data_creation(self):
        """Test that weather data can be created."""
        self.assertEqual(self.weather_data.location_name, 'Lusaka, Zambia')
        self.assertEqual(self.weather_data.temperature, Decimal('25.5'))
        self.assertEqual(self.weather_data.weather_condition, 'Clear')
        self.assertFalse(self.weather_data.is_stale)

    def test_wind_direction_cardinal(self):
        """Test wind direction cardinal conversion."""
        # North
        self.weather_data.wind_direction = 0
        self.assertEqual(self.weather_data.get_wind_direction_cardinal(), 'N')

        # East
        self.weather_data.wind_direction = 90
        self.assertEqual(self.weather_data.get_wind_direction_cardinal(), 'E')

        # South
        self.weather_data.wind_direction = 180
        self.assertEqual(self.weather_data.get_wind_direction_cardinal(), 'S')

        # West
        self.weather_data.wind_direction = 270
        self.assertEqual(self.weather_data.get_wind_direction_cardinal(), 'W')

    def test_stale_data(self):
        """Test stale data detection."""
        # Fresh data should not be stale
        self.assertFalse(self.weather_data.is_stale)

        # Make data old using update to avoid auto_now
        old_time = timezone.now() - timedelta(minutes=35)
        WeatherData.objects.filter(id=self.weather_data.id).update(updated_at=old_time)

        # Refresh from database to get updated timestamp
        self.weather_data.refresh_from_db()
        self.assertTrue(self.weather_data.is_stale)


class WeatherForecastModelTest(TestCase):
    """
    Test cases for WeatherForecast model.
    """

    def setUp(self):
        self.forecast = WeatherForecast.objects.create(
            latitude=Decimal('-15.3875'),
            longitude=Decimal('28.3228'),
            location_name='Lusaka, Zambia',
            forecast_date=timezone.now().date() + timedelta(days=1),
            forecast_time=timezone.now().time(),
            temperature_min=Decimal('20.0'),
            temperature_max=Decimal('28.0'),
            humidity=70,
            pressure=1010,
            wind_speed=Decimal('4.0'),
            wind_direction=200,
            weather_condition='Clouds',
            weather_description='few clouds',
            weather_icon='02d',
            precipitation_probability=Decimal('20.0'),
            rainfall_amount=Decimal('0.5'),
            data_source='openweathermap',
            api_response={'test': 'forecast_data'}
        )

    def test_forecast_creation(self):
        """Test that forecast data can be created."""
        self.assertEqual(self.forecast.location_name, 'Lusaka, Zambia')
        self.assertEqual(self.forecast.temperature_max, Decimal('28.0'))
        self.assertEqual(self.forecast.precipitation_probability, Decimal('20.0'))


class WeatherAlertModelTest(TestCase):
    """
    Test cases for WeatherAlert model.
    """

    def setUp(self):
        self.alert = WeatherAlert.objects.create(
            latitude=Decimal('-15.3875'),
            longitude=Decimal('28.3228'),
            location_name='Lusaka, Zambia',
            alert_type='Heavy Rain',
            severity='moderate',
            title='Heavy Rainfall Warning',
            description='Expect heavy rainfall in the next 24 hours',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=24),
            is_active=True,
            data_source='openweathermap',
            api_response={'test': 'alert_data'}
        )

    def test_alert_creation(self):
        """Test that alert can be created."""
        self.assertEqual(self.alert.alert_type, 'Heavy Rain')
        self.assertEqual(self.alert.severity, 'moderate')
        self.assertTrue(self.alert.is_active)
        self.assertFalse(self.alert.is_expired)

    def test_expired_alert(self):
        """Test expired alert detection."""
        # Make alert expired
        self.alert.end_time = timezone.now() - timedelta(hours=1)
        self.alert.save()
        self.assertTrue(self.alert.is_expired)

    def test_duration_calculation(self):
        """Test alert duration calculation."""
        expected_duration = 24.0  # 24 hours
        self.assertEqual(self.alert.duration_hours, expected_duration)


class WeatherSerializerTest(TestCase):
    """
    Test cases for weather serializers.
    """

    def setUp(self):
        self.weather_data = WeatherData.objects.create(
            latitude=Decimal('-15.3875'),
            longitude=Decimal('28.3228'),
            location_name='Lusaka, Zambia',
            temperature=Decimal('25.5'),
            feels_like=Decimal('27.0'),  # Required field
            humidity=65,
            pressure=1013,  # Required field
            wind_speed=Decimal('3.5'),  # Required field
            wind_direction=180,
            weather_condition='Clear',
            weather_description='clear sky',
            weather_icon='01d',
            rainfall_1h=Decimal('0.0'),
            rainfall_3h=Decimal('0.0'),
            data_source='openweathermap',
            api_response={'test': 'data'}
        )

    def test_weather_data_serializer(self):
        """Test WeatherData serializer."""
        serializer = WeatherDataSerializer(self.weather_data)
        data = serializer.data

        self.assertEqual(data['temperature'], '25.50')
        self.assertEqual(data['location_name'], 'Lusaka, Zambia')
        self.assertEqual(data['wind_direction_cardinal'], 'S')  # 180 degrees = South

    def test_weather_forecast_serializer(self):
        """Test WeatherForecast serializer."""
        forecast = WeatherForecast.objects.create(
            latitude=Decimal('-15.3875'),
            longitude=Decimal('28.3228'),
            forecast_date=timezone.now().date(),
            forecast_time=timezone.now().time(),
            temperature_min=Decimal('20.0'),
            temperature_max=Decimal('28.0'),
            humidity=70,  # Required field
            pressure=1010,  # Required field
            wind_speed=Decimal('4.0'),  # Required field
            wind_direction=200,  # Required field
            weather_condition='Clouds',
            weather_description='few clouds',
            weather_icon='02d',
            precipitation_probability=Decimal('20.0'),
            rainfall_amount=Decimal('0.5'),
            data_source='openweathermap',
            api_response={'test': 'forecast_data'}
        )

        serializer = WeatherForecastSerializer(forecast)
        data = serializer.data

        self.assertEqual(data['temperature_min'], '20.00')
        self.assertEqual(data['temperature_max'], '28.00')


class WeatherServiceTest(TestCase):
    """
    Test cases for weather services.
    Uses mock data when no API key is available.
    """

    def setUp(self):
        # No longer skip tests - we support mock data
        pass

    def test_openweathermap_service_initialization(self):
        """Test OpenWeatherMap service initialization."""
        service = OpenWeatherMapService()
        self.assertIsNotNone(service)

    def test_openweathermap_service_no_api_key(self):
        """Test service works with mock data when no API key is available."""
        import os
        # Temporarily remove API key
        original_key = os.environ.get('OPENWEATHERMAP_API_KEY')
        if 'OPENWEATHERMAP_API_KEY' in os.environ:
            del os.environ['OPENWEATHERMAP_API_KEY']

        # Should initialize and use mock data
        service = OpenWeatherMapService()
        self.assertIsNotNone(service)
        self.assertIsNone(service.api_key)

        # Test that mock data is returned
        weather_data = service.get_current_weather(-15.3875, 28.3228)
        self.assertIsNotNone(weather_data)
        self.assertEqual(weather_data.data_source, 'mock_data')

        # Restore API key
        if original_key:
            os.environ['OPENWEATHERMAP_API_KEY'] = original_key

    def test_weather_service_initialization(self):
        """Test WeatherService initialization."""
        service = WeatherService()
        self.assertIsNotNone(service)
