from django.contrib import admin
from .models import Field


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    """Admin interface for Field model."""
    
    list_display = [
        'name',
        'user',
        'crop_type',
        'crop_age_weeks',
        'area',
        'soil_type',
        'current_soil_moisture',
        'is_active',
        'created_at',
    ]
    
    list_filter = [
        'crop_type',
        'soil_type',
        'irrigation_method',
        'current_season',
        'is_active',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'location',
        'region',
        'user__email',
        'user__name',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'crop_days',
        'crop_age_weeks',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'is_active')
        }),
        ('Location', {
            'fields': ('location', 'region', 'latitude', 'longitude')
        }),
        ('Field Details', {
            'fields': ('area', 'irrigation_method')
        }),
        ('Crop Information', {
            'fields': ('crop_type', 'planting_date', 'crop_days', 'crop_age_weeks')
        }),
        ('Soil Information', {
            'fields': ('soil_type', 'current_soil_moisture')
        }),
        ('Season', {
            'fields': ('current_season',)
        }),
        ('Additional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def crop_age_weeks(self, obj):
        """Display crop age in weeks."""
        return f"{obj.crop_age_weeks} weeks"
    crop_age_weeks.short_description = 'Crop Age'
