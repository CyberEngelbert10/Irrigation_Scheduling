from rest_framework import serializers
from .models import IrrigationSchedule, IrrigationHistory


class IrrigationScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for IrrigationSchedule model.
    """

    field_name = serializers.CharField(source='field.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_scheduled = serializers.IntegerField(read_only=True)

    class Meta:
        model = IrrigationSchedule
        fields = [
            'id', 'field', 'field_name', 'user', 'user_email',
            'predicted_water_amount', 'confidence_score', 'irrigation_reason',
            'recommended_date', 'recommended_time', 'priority_level', 'status',
            'model_input_data', 'model_prediction_details',
            'created_at', 'updated_at', 'scheduled_at',
            'is_overdue', 'days_until_scheduled'
        ]
        read_only_fields = [
            'id', 'confidence_score', 'model_input_data',
            'model_prediction_details', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        """
        Validate that the recommended date/time is in the future for new schedules.
        """
        if self.instance is None:  # Only for new instances
            from django.utils import timezone
            recommended_datetime = timezone.datetime.combine(
                data['recommended_date'],
                data['recommended_time'],
                tzinfo=timezone.get_current_timezone()
            )
            if recommended_datetime <= timezone.now():
                raise serializers.ValidationError(
                    "Recommended date and time must be in the future."
                )
        return data


class IrrigationScheduleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new irrigation schedules (used by AI service).
    """

    class Meta:
        model = IrrigationSchedule
        fields = [
            'field', 'user', 'predicted_water_amount', 'confidence_score',
            'irrigation_reason', 'recommended_date', 'recommended_time',
            'priority_level', 'model_input_data', 'model_prediction_details'
        ]

    def create(self, validated_data):
        # Set status to 'pending' by default
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class IrrigationScheduleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating irrigation schedule status.
    """

    class Meta:
        model = IrrigationSchedule
        fields = ['status', 'scheduled_at']
        read_only_fields = ['scheduled_at']

    def update(self, instance, validated_data):
        status = validated_data.get('status', instance.status)

        # Auto-set scheduled_at when status changes to completed
        if status == 'completed' and instance.status != 'completed':
            from django.utils import timezone
            validated_data['scheduled_at'] = timezone.now()

        return super().update(instance, validated_data)


class IrrigationHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for IrrigationHistory model.
    """

    field_name = serializers.CharField(source='field.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    schedule_details = serializers.SerializerMethodField()

    class Meta:
        model = IrrigationHistory
        fields = [
            'id', 'field', 'field_name', 'user', 'user_email',
            'water_amount_used', 'irrigation_method',
            'irrigation_date', 'irrigation_time', 'duration_minutes',
            'weather_conditions', 'soil_moisture_before', 'soil_moisture_after',
            'notes', 'effectiveness_rating', 'related_schedule', 'schedule_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_schedule_details(self, obj):
        """Get details of related schedule if exists."""
        if obj.related_schedule:
            return {
                'id': obj.related_schedule.id,
                'predicted_amount': obj.related_schedule.predicted_water_amount,
                'confidence_score': obj.related_schedule.confidence_score,
                'status': obj.related_schedule.status
            }
        return None


class IrrigationHistoryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating irrigation history records.
    """

    class Meta:
        model = IrrigationHistory
        fields = [
            'field', 'user', 'water_amount_used', 'irrigation_method',
            'irrigation_date', 'irrigation_time', 'duration_minutes',
            'weather_conditions', 'soil_moisture_before', 'soil_moisture_after',
            'notes', 'effectiveness_rating', 'related_schedule'
        ]

    def validate(self, data):
        """
        Validate irrigation date is not in the future.
        """
        from django.utils import timezone
        irrigation_datetime = timezone.datetime.combine(
            data['irrigation_date'],
            data['irrigation_time'],
            tzinfo=timezone.get_current_timezone()
        )
        if irrigation_datetime > timezone.now():
            raise serializers.ValidationError(
                "Irrigation date and time cannot be in the future."
            )
        return data