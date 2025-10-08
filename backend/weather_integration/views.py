from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import WeatherData, WeatherForecast, WeatherAlert
from .serializers import (
    WeatherDataSerializer, WeatherForecastSerializer, WeatherAlertSerializer,
    WeatherDataCreateSerializer, WeatherForecastCreateSerializer
)
from .services import WeatherService


class WeatherDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving cached weather data.
    """
    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get current weather data for specific coordinates",
        request_body=WeatherDataCreateSerializer,
        responses={200: WeatherDataSerializer}
    )
    @action(detail=False, methods=['post'])
    def current(self, request):
        """
        Get current weather data for given coordinates.
        Creates new data if not cached or stale.
        """
        serializer = WeatherDataCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        latitude = serializer.validated_data['latitude']
        longitude = serializer.validated_data['longitude']
        location_name = serializer.validated_data.get('location_name')

        weather_service = WeatherService()
        weather_data = weather_service.get_current_weather(latitude, longitude)

        if weather_data:
            # Update location name if provided
            if location_name and not weather_data.location_name:
                weather_data.location_name = location_name
                weather_data.save()

            serializer = WeatherDataSerializer(weather_data)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "Failed to fetch weather data"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class WeatherForecastViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving weather forecast data.
    """
    queryset = WeatherForecast.objects.all()
    serializer_class = WeatherForecastSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get weather forecast for specific coordinates",
        request_body=WeatherForecastCreateSerializer,
        responses={200: WeatherForecastSerializer(many=True)}
    )
    @action(detail=False, methods=['post'])
    def forecast(self, request):
        """
        Get weather forecast for given coordinates.
        """
        serializer = WeatherForecastCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        latitude = serializer.validated_data['latitude']
        longitude = serializer.validated_data['longitude']
        days = serializer.validated_data.get('days', 5)

        weather_service = WeatherService()
        forecasts = weather_service.get_weather_forecast(latitude, longitude, days)

        if forecasts:
            serializer = WeatherForecastSerializer(forecasts, many=True)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "Failed to fetch forecast data"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class WeatherAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving weather alerts.
    """
    queryset = WeatherAlert.objects.filter(is_active=True)
    serializer_class = WeatherAlertSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get active weather alerts for specific coordinates",
        manual_parameters=[
            openapi.Parameter(
                'latitude', openapi.IN_QUERY,
                description="Latitude coordinate",
                type=openapi.TYPE_NUMBER,
                required=True
            ),
            openapi.Parameter(
                'longitude', openapi.IN_QUERY,
                description="Longitude coordinate",
                type=openapi.TYPE_NUMBER,
                required=True
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """
        Get active weather alerts for given coordinates.
        """
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')

        if not latitude or not longitude:
            return Response(
                {"error": "latitude and longitude parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat = float(latitude)
            lon = float(longitude)
        except ValueError:
            return Response(
                {"error": "Invalid latitude or longitude values"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # For now, return empty list as alerts require paid OpenWeatherMap plan
        alerts = WeatherAlert.objects.filter(
            latitude__range=(lat-1, lat+1),
            longitude__range=(lon-1, lon+1),
            is_active=True
        )

        serializer = WeatherAlertSerializer(alerts, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_weather_data(request):
    """
    Force refresh weather data for given coordinates.
    """
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    if not latitude or not longitude:
        return Response(
            {"error": "latitude and longitude are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        lat = float(latitude)
        lon = float(longitude)
    except ValueError:
        return Response(
            {"error": "Invalid latitude or longitude values"},
            status=status.HTTP_400_BAD_REQUEST
        )

    weather_service = WeatherService()

    # Clear cache
    cache_key_current = f"weather_current_{lat}_{lon}"
    cache_key_forecast = f"weather_forecast_{lat}_{lon}_5"
    cache.delete(cache_key_current)
    cache.delete(cache_key_forecast)

    # Fetch fresh data
    weather_data = weather_service.get_current_weather(lat, lon, force_refresh=True)
    forecasts = weather_service.get_weather_forecast(lat, lon, force_refresh=True)

    response_data = {}

    if weather_data:
        response_data['current_weather'] = WeatherDataSerializer(weather_data).data

    if forecasts:
        response_data['forecast'] = WeatherForecastSerializer(forecasts, many=True).data

    if not response_data:
        return Response(
            {"error": "Failed to refresh weather data"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weather_summary(request):
    """
    Get a summary of weather data for dashboard display.
    """
    # Get user's fields and their weather data
    # This would integrate with the fields app to get field locations
    # For now, return a placeholder response

    return Response({
        "message": "Weather summary endpoint - integrate with fields app to get location-specific data",
        "note": "This endpoint will aggregate weather data for all user's fields"
    })


class WeatherStatsView(APIView):
    """
    View for weather statistics and analytics.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get weather statistics for a location",
        manual_parameters=[
            openapi.Parameter(
                'latitude', openapi.IN_QUERY,
                description="Latitude coordinate",
                type=openapi.TYPE_NUMBER,
                required=True
            ),
            openapi.Parameter(
                'longitude', openapi.IN_QUERY,
                description="Longitude coordinate",
                type=openapi.TYPE_NUMBER,
                required=True
            ),
            openapi.Parameter(
                'days', openapi.IN_QUERY,
                description="Number of days to analyze (default: 7)",
                type=openapi.TYPE_INTEGER,
                default=7
            ),
        ]
    )
    def get(self, request):
        """
        Get weather statistics for irrigation planning.
        """
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        days = int(request.query_params.get('days', 7))

        if not latitude or not longitude:
            return Response(
                {"error": "latitude and longitude parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat = float(latitude)
            lon = float(longitude)
        except ValueError:
            return Response(
                {"error": "Invalid latitude or longitude values"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get forecast data for statistics
        weather_service = WeatherService()
        forecasts = weather_service.get_weather_forecast(lat, lon, days)

        if not forecasts:
            return Response(
                {"error": "No forecast data available"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Calculate statistics
        temps_min = [f.temperature_min for f in forecasts]
        temps_max = [f.temperature_max for f in forecasts]
        humidities = [f.humidity for f in forecasts]
        precip_probs = [f.precipitation_probability for f in forecasts]

        stats = {
            'temperature': {
                'min': min(temps_min),
                'max': max(temps_max),
                'avg': sum(temps_min + temps_max) / (2 * len(forecasts))
            },
            'humidity': {
                'min': min(humidities),
                'max': max(humidities),
                'avg': sum(humidities) / len(humidities)
            },
            'precipitation': {
                'max_probability': max(precip_probs),
                'avg_probability': sum(precip_probs) / len(precip_probs),
                'days_with_rain': len([p for p in precip_probs if p > 30])  # Days with >30% rain chance
            },
            'forecast_days': len(forecasts),
            'location': forecasts[0].location_name if forecasts else None
        }

        return Response(stats)
