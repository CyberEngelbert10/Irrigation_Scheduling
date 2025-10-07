from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


class Field(models.Model):
    """
    Represents a farmer's field with crop and soil information.
    Contains all data needed for AI irrigation prediction model.
    """
    
    # Zambian Region Choices - 10 Provinces
    REGION_CHOICES = [
        ('lusaka', 'Lusaka'),
        ('central', 'Central Province'),
        ('southern', 'Southern Province'),
        ('eastern', 'Eastern Province'),
        ('copperbelt', 'Copperbelt'),
        ('northern', 'Northern Province'),
        ('western', 'Western Province'),
        ('luapula', 'Luapula'),
        ('muchinga', 'Muchinga'),
        ('northwestern', 'North-Western'),
    ]
    
    # Crop Type Choices - Based on AI model requirements (6 crops supported)
    CROP_CHOICES = [
        ('Maize', 'Maize'),
        ('Wheat', 'Wheat'),
        ('Rice', 'Rice'),
        ('Tomatoes', 'Tomatoes'),
        ('Potatoes', 'Potatoes'),
        ('Cotton', 'Cotton'),
    ]
    
    # Soil Type Choices - Based on AI model requirements (4 common Zambian soils)
    SOIL_CHOICES = [
        ('Clay', 'Clay'),
        ('Loam', 'Loam'),
        ('Sandy', 'Sandy'),
        ('Silty', 'Silty'),
    ]
    
    # Irrigation Method Choices - Common in Zambia
    IRRIGATION_CHOICES = [
        ('drip', 'Drip Irrigation'),
        ('sprinkler', 'Sprinkler Irrigation'),
        ('flood', 'Flood/Furrow Irrigation'),
        ('rainfed', 'Rain-fed (No Irrigation)'),
    ]
    
    # Season Choices - Based on AI model requirements (Zambian seasons)
    SEASON_CHOICES = [
        ('Dry', 'Dry Season (May-October)'),
        ('Wet', 'Wet Season (November-April)'),
    ]
    
    # Basic Field Information
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='fields',
        help_text='Owner of this field'
    )
    name = models.CharField(
        max_length=100,
        help_text='Field name or identifier (e.g., "North Field", "Plot 1")'
    )
    
    # Location Information
    location = models.CharField(
        max_length=200,
        help_text='Detailed field location (e.g., "Chilanga District, Lusaka")',
        blank=True
    )
    region = models.CharField(
        max_length=50,
        choices=REGION_CHOICES,
        default='lusaka',
        help_text='Zambian province where the field is located'
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Latitude for precise weather data'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Longitude for precise weather data'
    )
    
    # Field Size
    area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='Field area in hectares'
    )
    
    # Crop Information - Required for AI Model
    crop_type = models.CharField(
        max_length=50,
        choices=CROP_CHOICES,
        help_text='Type of crop planted in this field'
    )
    planting_date = models.DateField(
        help_text='Date when the crop was planted'
    )
    
    # Soil Information - Required for AI Model
    soil_type = models.CharField(
        max_length=50,
        choices=SOIL_CHOICES,
        help_text='Primary soil type in this field'
    )
    current_soil_moisture = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=50,
        help_text='Current soil moisture percentage (0-100%)'
    )
    
    # Irrigation Information
    irrigation_method = models.CharField(
        max_length=50,
        choices=IRRIGATION_CHOICES,
        default='rainfed',
        help_text='Primary irrigation method used'
    )
    
    # Season Information - Required for AI Model
    current_season = models.CharField(
        max_length=50,
        choices=SEASON_CHOICES,
        default='Dry',
        help_text='Current growing season'
    )
    
    # Additional Information
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about this field'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this field is currently in use'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Field'
        verbose_name_plural = 'Fields'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_crop_type_display()}) - {self.user.email}"
    
    @property
    def crop_days(self):
        """Calculate days since planting - Required for AI Model"""
        if self.planting_date:
            delta = timezone.now().date() - self.planting_date
            return delta.days
        return 0
    
    @property
    def crop_age_weeks(self):
        """Get crop age in weeks for display"""
        return self.crop_days // 7
    
    def update_soil_moisture(self, moisture_value):
        """Update soil moisture reading"""
        if 0 <= moisture_value <= 100:
            self.current_soil_moisture = moisture_value
            self.save(update_fields=['current_soil_moisture', 'updated_at'])
            return True
        return False
    
    def get_ai_model_input(self, weather_data):
        """
        Prepare data for AI model prediction.
        Returns dict with all 10 required features matching AI model exactly.
        
        Args:
            weather_data (dict): Current weather data with keys:
                - temperature (°C)
                - humidity (%)
                - rainfall (mm)
                - windspeed (km/h)
        
        Returns:
            dict: Dictionary with all 10 AI model input features
        """
        return {
            'CropType': self.crop_type,  # Direct value: 'Maize', 'Wheat', etc.
            'CropDays': self.crop_days,
            'SoilMoisture': self.current_soil_moisture,
            'temperature': weather_data.get('temperature', 25),
            'humidity': weather_data.get('humidity', 60),
            'rainfall': weather_data.get('rainfall', 0),
            'windspeed': weather_data.get('windspeed', 10),
            'soilType': self.soil_type,  # Direct value: 'Clay', 'Loam', etc.
            'region': self.get_region_display(),  # 'Lusaka', 'Central Province', etc.
            'season': self.current_season,  # Direct value: 'Dry', 'Wet'
        }
