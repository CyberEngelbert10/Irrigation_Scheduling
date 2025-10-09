from django.contrib import admin
from .models import IrrigationSchedule, IrrigationHistory


@admin.register(IrrigationSchedule)
class IrrigationScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'field', 'user', 'recommended_date', 'recommended_time',
        'predicted_water_amount', 'priority_level', 'status', 'is_overdue'
    ]
    list_filter = [
        'status', 'priority_level', 'recommended_date',
        'field__crop_type', 'field__region'
    ]
    search_fields = [
        'field__name', 'user__email', 'irrigation_reason'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'confidence_score',
        'model_input_data', 'model_prediction_details'
    ]
    ordering = ['-recommended_date', '-recommended_time']

    fieldsets = (
        ('Field & User', {
            'fields': ('field', 'user')
        }),
        ('AI Prediction', {
            'fields': (
                'predicted_water_amount', 'confidence_score',
                'irrigation_reason', 'model_input_data', 'model_prediction_details'
            )
        }),
        ('Schedule', {
            'fields': (
                'recommended_date', 'recommended_time',
                'priority_level', 'status', 'scheduled_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('field', 'user')


@admin.register(IrrigationHistory)
class IrrigationHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'field', 'user', 'irrigation_date', 'irrigation_time',
        'water_amount_used', 'irrigation_method', 'effectiveness_rating'
    ]
    list_filter = [
        'irrigation_method', 'irrigation_date',
        'field__crop_type', 'field__region', 'effectiveness_rating'
    ]
    search_fields = [
        'field__name', 'user__email', 'notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-irrigation_date', '-irrigation_time']

    fieldsets = (
        ('Field & User', {
            'fields': ('field', 'user')
        }),
        ('Irrigation Details', {
            'fields': (
                'water_amount_used', 'irrigation_method',
                'irrigation_date', 'irrigation_time', 'duration_minutes'
            )
        }),
        ('Conditions', {
            'fields': (
                'weather_conditions', 'soil_moisture_before', 'soil_moisture_after'
            )
        }),
        ('Feedback', {
            'fields': ('notes', 'effectiveness_rating', 'related_schedule')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'field', 'user', 'related_schedule'
        )
