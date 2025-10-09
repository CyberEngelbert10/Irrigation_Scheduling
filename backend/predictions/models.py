from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.fields.models import Field

User = get_user_model()


class IrrigationSchedule(models.Model):
    """
    Model to store AI-generated irrigation schedules for fields.
    """

    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='irrigation_schedules'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='irrigation_schedules'
    )

    # AI prediction data
    predicted_water_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Predicted water amount in liters"
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        help_text="AI model confidence score (0-1)"
    )
    irrigation_reason = models.TextField(
        help_text="Explanation of why this irrigation is recommended"
    )

    # Schedule timing
    recommended_date = models.DateField(
        help_text="Recommended date for irrigation"
    )
    recommended_time = models.TimeField(
        help_text="Recommended time for irrigation"
    )
    priority_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Priority'),
            ('medium', 'Medium Priority'),
            ('high', 'High Priority'),
            ('critical', 'Critical Priority'),
        ],
        default='medium',
        help_text="Urgency level of the irrigation"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('completed', 'Completed'),
            ('skipped', 'Skipped'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending',
        help_text="Current status of the irrigation schedule"
    )

    # Model input data (for debugging and transparency)
    model_input_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Input data used for AI prediction"
    )
    model_prediction_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Detailed prediction output from AI model"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the irrigation was actually performed"
    )

    class Meta:
        verbose_name = "Irrigation Schedule"
        verbose_name_plural = "Irrigation Schedules"
        ordering = ['-recommended_date', '-recommended_time']
        indexes = [
            models.Index(fields=['field', 'status']),
            models.Index(fields=['user', 'recommended_date']),
            models.Index(fields=['status', 'recommended_date']),
        ]
        unique_together = ['field', 'recommended_date', 'recommended_time']

    def __str__(self):
        return f"{self.field.name} - {self.recommended_date} {self.recommended_time}"

    @property
    def is_overdue(self):
        """Check if the scheduled irrigation is overdue."""
        if self.status in ['completed', 'cancelled']:
            return False
        scheduled_datetime = timezone.datetime.combine(
            self.recommended_date,
            self.recommended_time,
            tzinfo=timezone.get_current_timezone()
        )
        return timezone.now() > scheduled_datetime

    @property
    def days_until_scheduled(self):
        """Calculate days until scheduled irrigation."""
        scheduled_datetime = timezone.datetime.combine(
            self.recommended_date,
            self.recommended_time,
            tzinfo=timezone.get_current_timezone()
        )
        delta = scheduled_datetime - timezone.now()
        return delta.days


class IrrigationHistory(models.Model):
    """
    Model to store historical irrigation records.
    """

    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='irrigation_history'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='irrigation_history'
    )

    # Actual irrigation data
    water_amount_used = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Actual water amount used in liters"
    )
    irrigation_method = models.CharField(
        max_length=50,
        choices=[
            ('drip', 'Drip Irrigation'),
            ('sprinkler', 'Sprinkler System'),
            ('flood', 'Flood Irrigation'),
            ('manual', 'Manual Watering'),
            ('other', 'Other'),
        ],
        help_text="Method used for irrigation"
    )

    # Timing
    irrigation_date = models.DateField(
        help_text="Date when irrigation was performed"
    )
    irrigation_time = models.TimeField(
        help_text="Time when irrigation was performed"
    )
    duration_minutes = models.PositiveIntegerField(
        help_text="Duration of irrigation in minutes"
    )

    # Conditions at time of irrigation
    weather_conditions = models.JSONField(
        null=True,
        blank=True,
        help_text="Weather conditions during irrigation"
    )
    soil_moisture_before = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Soil moisture before irrigation (%)"
    )
    soil_moisture_after = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Soil moisture after irrigation (%)"
    )

    # Notes and feedback
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the irrigation"
    )
    effectiveness_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Effectiveness rating (1-5)"
    )

    # Link to schedule if applicable
    related_schedule = models.ForeignKey(
        IrrigationSchedule,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='history_records',
        help_text="Related irrigation schedule if applicable"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Irrigation History"
        verbose_name_plural = "Irrigation Histories"
        ordering = ['-irrigation_date', '-irrigation_time']
        indexes = [
            models.Index(fields=['field', 'irrigation_date']),
            models.Index(fields=['user', 'irrigation_date']),
        ]

    def __str__(self):
        return f"{self.field.name} - {self.irrigation_date} {self.irrigation_time}"
