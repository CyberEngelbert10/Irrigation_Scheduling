from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta

from apps.fields.models import Field
from predictions.models import IrrigationHistory

User = get_user_model()


class AnalyticsAPITestCase(APITestCase):
    """
    Test cases for analytics API endpoints.
    """

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )

        self.field = Field.objects.create(
            user=self.user,
            name='Test Field',
            crop_type='Maize',
            region='lusaka',
            soil_type='Silty',
            area=1.0,
            current_soil_moisture=30.0,
            planting_date=timezone.now().date() - timedelta(days=60)
        )

        # Create some irrigation history
        base_date = timezone.now().date()
        for i in range(10):
            IrrigationHistory.objects.create(
                user=self.user,
                field=self.field,
                water_amount_used=50.0 + i * 5,
                irrigation_method='drip',
                irrigation_date=base_date - timedelta(days=i),
                irrigation_time='08:00:00',
                duration_minutes=30,
                soil_moisture_before=30.0 + i,
                soil_moisture_after=70.0 + i,
                effectiveness_rating=min(5, 3 + (i % 3)),
                notes=f'Test irrigation {i}'
            )

    def test_water_usage_stats(self):
        """Test water usage statistics endpoint."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/analytics/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn('total_water_usage', data)
        self.assertIn('average_daily_usage', data)
        self.assertIn('usage_by_field', data)
        self.assertIn('usage_by_method', data)
        self.assertIn('monthly_trends', data)
        self.assertIn('efficiency_metrics', data)
        self.assertIn('usage_trend', data)

        # Check that we have data
        self.assertGreater(data['total_water_usage'], 0)
        self.assertGreater(len(data['usage_by_field']), 0)

    def test_field_analytics(self):
        """Test field-specific analytics endpoint."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/analytics/field/{self.field.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['field_id'], self.field.id)
        self.assertEqual(data['field_name'], self.field.name)
        self.assertIn('total_water_usage', data)
        self.assertIn('irrigation_count', data)
        self.assertIn('soil_moisture_trends', data)
        self.assertIn('weekly_usage', data)

    def test_field_analytics_unauthorized(self):
        """Test that users can't access other users' field analytics."""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            name='Other User'
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.get(f'/api/analytics/field/{self.field.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_efficiency_report(self):
        """Test irrigation efficiency report endpoint."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/analytics/efficiency/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn('efficiency_analysis', data)
        self.assertIn('best_performing_methods', data)
        self.assertIn('recommendations', data)
        self.assertIn('summary', data)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users can't access analytics."""
        response = self.client.get('/api/analytics/stats/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
