import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from django.utils import timezone
from django.core.cache import cache
from .models import WeatherData, WeatherForecast, WeatherAlert

logger = logging.getLogger(__name__)


class OpenWeatherMapService:
    """
    Service class for interacting with OpenWeatherMap API.
    Handles current weather, forecast, and alerts data.
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL = "https://api.openweathermap.org/geo/1.0"

    def __init__(self):
        self.api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        # Treat placeholder values as no API key
        if not self.api_key or self.api_key.startswith('your-') or self.api_key == '':
            self.api_key = None
            import logging
            logging.warning("OPENWEATHERMAP_API_KEY not found or is placeholder. Using mock weather data for testing.")
        else:
            import logging
            logging.info("OpenWeatherMap API key found. Using real weather data.")

    def _make_request(self, url: str, params: Dict[str, Any]) -> Optional[Dict]:
        """
        Make a request to the OpenWeatherMap API with error handling.
        """
        try:
            params['appid'] = self.api_key
            params['units'] = 'metric'  # Use Celsius

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"OpenWeatherMap API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in OpenWeatherMap API call: {e}")
            return None

    def get_current_weather(self, latitude: float, longitude: float) -> Optional[WeatherData]:
        """
        Fetch current weather data for given coordinates.
        Returns WeatherData object or None if failed.
        """
        if not self.api_key:
            return self._get_mock_current_weather(latitude, longitude)

        cache_key = f"weather_current_{latitude}_{longitude}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        url = f"{self.BASE_URL}/weather"
        params = {
            'lat': latitude,
            'lon': longitude,
        }

        response = self._make_request(url, params)
        if not response:
            return None

        try:
            # Extract location name
            location_name = response.get('name', '')
            if not location_name and 'sys' in response:
                country = response['sys'].get('country', '')
                if country:
                    location_name = f"Lat {latitude}, Lon {longitude} ({country})"
                else:
                    location_name = f"Lat {latitude}, Lon {longitude}"

            weather_data = WeatherData.objects.create(
                latitude=latitude,
                longitude=longitude,
                location_name=location_name,
                temperature=response['main']['temp'],
                feels_like=response['main']['feels_like'],
                humidity=response['main']['humidity'],
                pressure=response['main']['pressure'],
                wind_speed=response['wind']['speed'],
                wind_direction=response['wind'].get('deg', 0),
                weather_condition=response['weather'][0]['main'],
                weather_description=response['weather'][0]['description'],
                weather_icon=response['weather'][0]['icon'],
                rainfall_1h=response.get('rain', {}).get('1h', 0),
                rainfall_3h=response.get('rain', {}).get('3h', 0),
                data_source='openweathermap',
                api_response=response
            )

            # Cache for 30 minutes
            cache.set(cache_key, weather_data, 1800)

            return weather_data

        except KeyError as e:
            logger.error(f"Missing expected key in OpenWeatherMap response: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return None

    def _get_mock_current_weather(self, latitude: float, longitude: float) -> WeatherData:
        """
        Return mock weather data for testing when no API key is available.
        """
        from datetime import datetime

        # Mock data for Lusaka, Zambia (typical October weather)
        mock_response = {
            'name': 'Lusaka',
            'main': {
                'temp': 28.5,
                'feels_like': 30.2,
                'humidity': 65,
                'pressure': 1013
            },
            'wind': {
                'speed': 3.2,
                'deg': 180
            },
            'weather': [{
                'main': 'Clear',
                'description': 'clear sky',
                'icon': '01d'
            }],
            'rain': {'1h': 0, '3h': 0}
        }

        return WeatherData.objects.create(
            latitude=latitude,
            longitude=longitude,
            location_name='Lusaka, Zambia',
            temperature=str(mock_response['main']['temp']),
            feels_like=str(mock_response['main']['feels_like']),
            humidity=mock_response['main']['humidity'],
            pressure=mock_response['main']['pressure'],
            wind_speed=str(mock_response['wind']['speed']),
            wind_direction=mock_response['wind']['deg'],
            weather_condition=mock_response['weather'][0]['main'],
            weather_description=mock_response['weather'][0]['description'],
            weather_icon=mock_response['weather'][0]['icon'],
            rainfall_1h=str(mock_response['rain']['1h']),
            rainfall_3h=str(mock_response['rain']['3h']),
            data_source='mock_data',
            api_response=mock_response
        )

    def get_weather_forecast(self, latitude: float, longitude: float, days: int = 5) -> List[WeatherForecast]:
        """
        Fetch weather forecast for given coordinates.
        Returns list of WeatherForecast objects.
        """
        if not self.api_key:
            return self._get_mock_forecast(latitude, longitude, days)

        cache_key = f"weather_forecast_{latitude}_{longitude}_{days}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        url = f"{self.BASE_URL}/forecast"
        params = {
            'lat': latitude,
            'lon': longitude,
            'cnt': min(days * 8, 40)  # 8 forecasts per day, max 40
        }

        response = self._make_request(url, params)
        if not response:
            return []

        try:
            forecasts = []
            location_name = response.get('city', {}).get('name', f"Lat {latitude}, Lon {longitude}")

            for item in response['list']:
                forecast_time = datetime.fromtimestamp(item['dt'])

                # Try to get existing forecast, create if doesn't exist
                try:
                    forecast = WeatherForecast.objects.get(
                        latitude=latitude,
                        longitude=longitude,
                        forecast_date=forecast_time.date(),
                        forecast_time=forecast_time.time()
                    )
                    # Update existing record
                    forecast.location_name = location_name
                    forecast.temperature_min = item['main']['temp_min']
                    forecast.temperature_max = item['main']['temp_max']
                    forecast.humidity = item['main']['humidity']
                    forecast.pressure = item['main']['pressure']
                    forecast.wind_speed = item['wind']['speed']
                    forecast.wind_direction = item['wind'].get('deg', 0)
                    forecast.weather_condition = item['weather'][0]['main']
                    forecast.weather_description = item['weather'][0]['description']
                    forecast.weather_icon = item['weather'][0]['icon']
                    forecast.precipitation_probability = item.get('pop', 0) * 100
                    forecast.rainfall_amount = item.get('rain', {}).get('3h', 0)
                    forecast.api_response = item
                    forecast.save()
                except WeatherForecast.DoesNotExist:
                    # Create new record
                    forecast = WeatherForecast.objects.create(
                        latitude=latitude,
                        longitude=longitude,
                        location_name=location_name,
                        forecast_date=forecast_time.date(),
                        forecast_time=forecast_time.time(),
                        temperature_min=item['main']['temp_min'],
                        temperature_max=item['main']['temp_max'],
                        humidity=item['main']['humidity'],
                        pressure=item['main']['pressure'],
                        wind_speed=item['wind']['speed'],
                        wind_direction=item['wind'].get('deg', 0),
                        weather_condition=item['weather'][0]['main'],
                        weather_description=item['weather'][0]['description'],
                        weather_icon=item['weather'][0]['icon'],
                        precipitation_probability=item.get('pop', 0) * 100,
                        rainfall_amount=item.get('rain', {}).get('3h', 0),
                        data_source='openweathermap',
                        api_response=item
                    )
                
                forecasts.append(forecast)

            # Cache for 1 hour
            cache.set(cache_key, forecasts, 3600)

            return forecasts

        except KeyError as e:
            logger.error(f"Missing expected key in forecast response: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing forecast data: {e}")
            return []

    def _get_mock_forecast(self, latitude: float, longitude: float, days: int) -> List[WeatherForecast]:
        """
        Return mock forecast data for testing.
        """
        from datetime import datetime, timedelta

        forecasts = []
        base_date = datetime.now()

        # Mock 7-day forecast with realistic Zambian October weather
        weather_scenarios = [
            ('Clear', 'clear sky', '01d', 28, 22),
            ('Clouds', 'few clouds', '02d', 27, 21),
            ('Clouds', 'scattered clouds', '03d', 26, 20),
            ('Rain', 'light rain', '10d', 25, 19),
            ('Clear', 'clear sky', '01d', 29, 23),
            ('Clear', 'clear sky', '01d', 30, 24),
            ('Clouds', 'broken clouds', '04d', 28, 22),
        ]

        for i in range(min(days, 7)):
            forecast_date = (base_date + timedelta(days=i)).date()
            scenario = weather_scenarios[i % len(weather_scenarios)]

            try:
                forecast = WeatherForecast.objects.get(
                    latitude=latitude,
                    longitude=longitude,
                    forecast_date=forecast_date,
                    forecast_time=datetime.strptime('12:00:00', '%H:%M:%S').time()
                )
                # Update existing record
                forecast.location_name = 'Lusaka, Zambia'
                forecast.temperature_min = str(scenario[4])
                forecast.temperature_max = str(scenario[3])
                forecast.humidity = 65 - (i * 2)
                forecast.pressure = 1013
                forecast.wind_speed = str(3.0 + (i * 0.5))
                forecast.wind_direction = 180 + (i * 10)
                forecast.weather_condition = scenario[0]
                forecast.weather_description = scenario[1]
                forecast.weather_icon = scenario[2]
                forecast.precipitation_probability = str(10 + (i * 5))
                forecast.rainfall_amount = str(i * 0.5)
                forecast.api_response = {'mock': f'day_{i+1}'}
                forecast.save()
            except WeatherForecast.DoesNotExist:
                # Create new record
                forecast = WeatherForecast.objects.create(
                    latitude=latitude,
                    longitude=longitude,
                    location_name='Lusaka, Zambia',
                    forecast_date=forecast_date,
                    forecast_time=datetime.strptime('12:00:00', '%H:%M:%S').time(),
                    temperature_min=str(scenario[4]),
                    temperature_max=str(scenario[3]),
                    humidity=65 - (i * 2),
                    pressure=1013,
                    wind_speed=str(3.0 + (i * 0.5)),
                    wind_direction=180 + (i * 10),
                    weather_condition=scenario[0],
                    weather_description=scenario[1],
                    weather_icon=scenario[2],
                    precipitation_probability=str(10 + (i * 5)),
                    rainfall_amount=str(i * 0.5),
                    data_source='mock_data',
                    api_response={'mock': f'day_{i+1}'}
                )
            
            forecasts.append(forecast)

        return forecasts

    def get_weather_alerts(self, latitude: float, longitude: float) -> List[WeatherAlert]:
        """
        Fetch weather alerts for given coordinates.
        Note: OpenWeatherMap One Call API 3.0 is required for alerts.
        """
        # This requires One Call API 3.0 which has different pricing
        # For now, return empty list as basic plan doesn't include alerts
        logger.info("Weather alerts require OpenWeatherMap One Call API 3.0 (paid plan)")
        return []

    def get_coordinates_by_city(self, city_name: str, country_code: str = None) -> Optional[Dict[str, float]]:
        """
        Get coordinates for a city name.
        Returns dict with 'lat' and 'lon' keys or None if not found.
        """
        url = f"{self.GEO_URL}/direct"
        params = {
            'q': f"{city_name},{country_code}" if country_code else city_name,
            'limit': 1
        }

        response = self._make_request(url, params)
        if not response or not response:
            return None

        try:
            location = response[0]
            return {
                'lat': location['lat'],
                'lon': location['lon']
            }
        except (KeyError, IndexError):
            return None

    def get_city_by_coordinates(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Get city name for given coordinates.
        """
        url = f"{self.GEO_URL}/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'limit': 1
        }

        response = self._make_request(url, params)
        if not response or not response:
            return None

        try:
            location = response[0]
            city = location.get('name', '')
            country = location.get('country', '')
            if city and country:
                return f"{city}, {country}"
            return city or f"Lat {latitude}, Lon {longitude}"
        except (KeyError, IndexError):
            return f"Lat {latitude}, Lon {longitude}"


class WeatherService:
    """
    High-level weather service that manages data freshness and caching.
    """

    def __init__(self):
        self.api_service = OpenWeatherMapService()

    def get_current_weather(self, latitude: float, longitude: float, force_refresh: bool = False) -> Optional[WeatherData]:
        """
        Get current weather data, using cache if available and fresh.
        """
        if not force_refresh:
            # Check for existing fresh data in database
            existing_data = WeatherData.objects.filter(
                latitude=latitude,
                longitude=longitude
            ).first()

            if existing_data and not existing_data.is_stale:
                return existing_data

        # Fetch fresh data
        return self.api_service.get_current_weather(latitude, longitude)

    def get_weather_forecast(self, latitude: float, longitude: float, days: int = 5, force_refresh: bool = False) -> List[WeatherForecast]:
        """
        Get weather forecast data.
        """
        if not force_refresh:
            # Check for existing forecast data (within last hour)
            cutoff_time = timezone.now() - timedelta(hours=1)
            existing_forecasts = WeatherForecast.objects.filter(
                latitude=latitude,
                longitude=longitude,
                forecast_date__gte=timezone.now().date(),
                updated_at__gte=cutoff_time
            ).order_by('forecast_date', 'forecast_time')

            if existing_forecasts.exists():
                return list(existing_forecasts)

        # Fetch fresh forecast data
        return self.api_service.get_weather_forecast(latitude, longitude, days)

    def cleanup_old_data(self):
        """
        Clean up old weather data to prevent database bloat.
        """
        # Delete weather data older than 24 hours
        cutoff_time = timezone.now() - timedelta(hours=24)
        WeatherData.objects.filter(updated_at__lt=cutoff_time).delete()

        # Delete forecast data older than 24 hours
        WeatherForecast.objects.filter(updated_at__lt=cutoff_time).delete()

        # Delete expired alerts
        WeatherAlert.objects.filter(end_time__lt=timezone.now()).delete()

        logger.info("Cleaned up old weather data")