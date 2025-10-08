from django.contrib import admin
from .models import WeatherData, WeatherForecast, WeatherAlert


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    """
    Admin interface for WeatherData model.
    """
    list_display = [
        'location_name', 'temperature', 'weather_condition',
        'humidity', 'wind_speed', 'updated_at', 'is_stale'
    ]
    list_filter = ['weather_condition', 'data_source', 'updated_at']
    search_fields = ['location_name', 'latitude', 'longitude']
    readonly_fields = ['id', 'created_at', 'updated_at', 'is_stale']
    ordering = ['-updated_at']

    fieldsets = (
        ('Location', {
            'fields': ('latitude', 'longitude', 'location_name')
        }),
        ('Weather Data', {
            'fields': (
                'temperature', 'feels_like', 'humidity', 'pressure',
                'wind_speed', 'wind_direction', 'weather_condition',
                'weather_description', 'weather_icon'
            )
        }),
        ('Precipitation', {
            'fields': ('rainfall_1h', 'rainfall_3h')
        }),
        ('Metadata', {
            'fields': ('data_source', 'api_response', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    """
    Admin interface for WeatherForecast model.
    """
    list_display = [
        'location_name', 'forecast_date', 'forecast_time',
        'temperature_max', 'temperature_min', 'weather_condition'
    ]
    list_filter = ['forecast_date', 'weather_condition', 'data_source']
    search_fields = ['location_name', 'latitude', 'longitude']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['forecast_date', 'forecast_time']

    fieldsets = (
        ('Location', {
            'fields': ('latitude', 'longitude', 'location_name')
        }),
        ('Forecast Time', {
            'fields': ('forecast_date', 'forecast_time')
        }),
        ('Temperature', {
            'fields': ('temperature_min', 'temperature_max')
        }),
        ('Weather Data', {
            'fields': (
                'humidity', 'pressure', 'wind_speed', 'wind_direction',
                'weather_condition', 'weather_description', 'weather_icon'
            )
        }),
        ('Precipitation', {
            'fields': ('precipitation_probability', 'rainfall_amount')
        }),
        ('Metadata', {
            'fields': ('data_source', 'api_response', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    """
    Admin interface for WeatherAlert model.
    """
    list_display = [
        'location_name', 'alert_type', 'severity', 'title',
        'start_time', 'end_time', 'is_active'
    ]
    list_filter = ['severity', 'alert_type', 'is_active', 'data_source']
    search_fields = ['location_name', 'title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'is_expired', 'duration_hours']
    ordering = ['-start_time']

    fieldsets = (
        ('Location', {
            'fields': ('latitude', 'longitude', 'location_name')
        }),
        ('Alert Information', {
            'fields': ('alert_type', 'severity', 'title', 'description')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'duration_hours')
        }),
        ('Status', {
            'fields': ('is_active', 'is_expired')
        }),
        ('Metadata', {
            'fields': ('data_source', 'api_response', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    actions = ['mark_as_active', 'mark_as_inactive']

    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} alerts marked as active.")
    mark_as_active.short_description = "Mark selected alerts as active"

    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} alerts marked as inactive.")
    mark_as_inactive.short_description = "Mark selected alerts as inactive"
