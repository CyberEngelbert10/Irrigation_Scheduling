from rest_framework import serializers
from django.utils import timezone
from .models import Field


class FieldSerializer(serializers.ModelSerializer):
    """
    Serializer for Field model with all CRUD operations.
    Automatically associates fields with the authenticated user.
    """
    
    # Read-only fields
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    crop_days = serializers.IntegerField(read_only=True)
    crop_age_weeks = serializers.IntegerField(read_only=True)
    crop_type_display = serializers.CharField(source='get_crop_type_display', read_only=True)
    soil_type_display = serializers.CharField(source='get_soil_type_display', read_only=True)
    region_display = serializers.CharField(source='get_region_display', read_only=True)
    irrigation_method_display = serializers.CharField(source='get_irrigation_method_display', read_only=True)
    season_display = serializers.CharField(source='get_current_season_display', read_only=True)
    
    class Meta:
        model = Field
        fields = [
            'id',
            'user_email',
            'user_name',
            'name',
            'location',
            'region',
            'region_display',
            'latitude',
            'longitude',
            'area',
            'crop_type',
            'crop_type_display',
            'planting_date',
            'crop_days',
            'crop_age_weeks',
            'soil_type',
            'soil_type_display',
            'current_soil_moisture',
            'irrigation_method',
            'irrigation_method_display',
            'current_season',
            'season_display',
            'notes',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_area(self, value):
        """Validate that area is positive."""
        if value <= 0:
            raise serializers.ValidationError("Area must be greater than 0.")
        return value
    
    def validate_current_soil_moisture(self, value):
        """Validate soil moisture is between 0-100."""
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Soil moisture must be between 0 and 100.")
        return value
    
    def validate_planting_date(self, value):
        """Validate planting date is not in the future."""
        if value > timezone.now().date():
            raise serializers.ValidationError("Planting date cannot be in the future.")
        return value


class FieldCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new field.
    Excludes user field as it will be set from request.user.
    """
    
    class Meta:
        model = Field
        fields = [
            'name',
            'location',
            'region',
            'latitude',
            'longitude',
            'area',
            'crop_type',
            'planting_date',
            'soil_type',
            'current_soil_moisture',
            'irrigation_method',
            'current_season',
            'notes',
            'is_active',
        ]
    
    def validate_area(self, value):
        """Validate that area is positive."""
        if value <= 0:
            raise serializers.ValidationError("Area must be greater than 0.")
        return value
    
    def validate_current_soil_moisture(self, value):
        """Validate soil moisture is between 0-100."""
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Soil moisture must be between 0 and 100.")
        return value
    
    def validate_planting_date(self, value):
        """Validate planting date is not in the future."""
        if value > timezone.now().date():
            raise serializers.ValidationError("Planting date cannot be in the future.")
        return value
    
    def create(self, validated_data):
        """Create field and associate with authenticated user."""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class FieldUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing field.
    Excludes user and timestamp fields.
    """
    
    class Meta:
        model = Field
        fields = [
            'name',
            'location',
            'region',
            'latitude',
            'longitude',
            'area',
            'crop_type',
            'planting_date',
            'soil_type',
            'current_soil_moisture',
            'irrigation_method',
            'current_season',
            'notes',
            'is_active',
        ]
    
    def validate_area(self, value):
        """Validate that area is positive."""
        if value <= 0:
            raise serializers.ValidationError("Area must be greater than 0.")
        return value
    
    def validate_current_soil_moisture(self, value):
        """Validate soil moisture is between 0-100."""
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Soil moisture must be between 0 and 100.")
        return value
    
    def validate_planting_date(self, value):
        """Validate planting date is not in the future."""
        if value > timezone.now().date():
            raise serializers.ValidationError("Planting date cannot be in the future.")
        return value


class SoilMoistureUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating only soil moisture.
    Used for quick moisture readings without full field update.
    """
    
    current_soil_moisture = serializers.IntegerField(
        min_value=0,
        max_value=100,
        help_text="Soil moisture percentage (0-100)"
    )
    
    def update(self, instance, validated_data):
        """Update soil moisture using the model's method."""
        moisture = validated_data.get('current_soil_moisture')
        instance.update_soil_moisture(moisture)
        return instance


class FieldListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for field list view.
    Includes only essential information for display.
    """
    
    crop_type_display = serializers.CharField(source='get_crop_type_display', read_only=True)
    region_display = serializers.CharField(source='get_region_display', read_only=True)
    crop_age_weeks = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Field
        fields = [
            'id',
            'name',
            'crop_type',
            'crop_type_display',
            'region',
            'region_display',
            'area',
            'crop_age_weeks',
            'current_soil_moisture',
            'is_active',
            'created_at',
        ]
