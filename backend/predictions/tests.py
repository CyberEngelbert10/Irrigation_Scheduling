import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
from apps.fields.models import Field
from .models import IrrigationSchedule, IrrigationHistory
from .services import IrrigationPredictionService
from .serializers import (
    IrrigationScheduleSerializer,
    IrrigationHistorySerializer,
    IrrigationScheduleCreateSerializer
)


class IrrigationScheduleModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.field = Field.objects.create(
            user=self.user,
            name='Test Field',
            crop_type='Maize',
            soil_type='Loam',
            region='central',
            current_season='Dry',
            area=1.0,
            latitude=-15.3875,
            longitude=28.3228,
            current_soil_moisture=35,
            planting_date=date.today() - timedelta(days=45)
        )

    def test_schedule_creation(self):
        schedule = IrrigationSchedule.objects.create(
            field=self.field,
            user=self.user,
            predicted_water_amount=25.5,
            confidence_score=0.85,
            irrigation_reason='Test irrigation',
            recommended_date=date.today() + timedelta(days=1),
            recommended_time=time(6, 0),
            priority_level='medium'
        )

        self.assertEqual(schedule.field, self.field)
        self.assertEqual(schedule.user, self.user)
        self.assertEqual(schedule.predicted_water_amount, Decimal('25.5'))
        self.assertEqual(schedule.status, 'pending')
        self.assertFalse(schedule.is_overdue)

    def test_overdue_schedule(self):
        past_date = date.today() - timedelta(days=1)
        schedule = IrrigationSchedule.objects.create(
            field=self.field,
            user=self.user,
            predicted_water_amount=25.0,
            confidence_score=0.8,
            irrigation_reason='Test irrigation',
            recommended_date=past_date,
            recommended_time=time(6, 0),
            priority_level='high'
        )

        self.assertTrue(schedule.is_overdue)


class IrrigationHistoryModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.field = Field.objects.create(
            user=self.user,
            name='Test Field',
            crop_type='Maize',
            soil_type='Loam',
            region='central',
            current_season='Dry',
            area=1.0,
            latitude=-15.3875,
            longitude=28.3228,
            current_soil_moisture=35,
            planting_date=date.today() - timedelta(days=45)
        )

    def test_history_creation(self):
        history = IrrigationHistory.objects.create(
            field=self.field,
            user=self.user,
            water_amount_used=22.5,
            irrigation_method='drip',
            irrigation_date=date.today(),
            irrigation_time=time(6, 30),
            duration_minutes=45,
            notes='Successful irrigation'
        )

        self.assertEqual(history.field, self.field)
        self.assertEqual(history.user, self.user)
        self.assertEqual(history.water_amount_used, Decimal('22.5'))
        self.assertEqual(history.irrigation_method, 'drip')


class IrrigationPredictionServiceTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.field = Field.objects.create(
            user=self.user,
            name='Test Field',
            crop_type='Maize',
            soil_type='Loam',
            region='central',
            current_season='Dry',
            area=1.0,
            latitude=-15.3875,
            longitude=28.3228,
            current_soil_moisture=35,
            planting_date=date.today() - timedelta(days=45)
        )

    @patch('predictions.services.IrrigationPredictionService._load_model')
    @patch('predictions.services.WeatherService')
    def test_predict_irrigation_need(self, mock_weather_service, mock_load_model):
        # Mock the model
        mock_model = MagicMock()
        mock_model.predict.return_value = [30.5]
        mock_model.predict_proba.return_value = [[0.2, 0.8]]

        # Mock weather service
        mock_weather_instance = MagicMock()
        mock_weather_instance.get_current_weather.return_value = {
            'temperature': 28.0,
            'humidity': 65.0,
            'rainfall': 0.0,
            'wind_speed': 3.5
        }
        mock_weather_service.return_value = mock_weather_instance

        service = IrrigationPredictionService()
        service.model = mock_model

        predicted_amount, confidence, input_data = service.predict_irrigation_need(self.field)

        self.assertEqual(predicted_amount, 30.5)
        self.assertEqual(confidence, 0.8)
        self.assertIn('CropType', input_data)
        self.assertIn('temperature', input_data)

    @patch('predictions.services.IrrigationPredictionService._load_model')
    @patch('predictions.services.WeatherService')
    def test_generate_irrigation_schedule(self, mock_weather_service, mock_load_model):
        # Mock the model
        mock_model = MagicMock()
        mock_model.predict.return_value = [25.0]
        mock_model.predict_proba.return_value = [[0.3, 0.7]]

        # Mock weather service
        mock_weather_instance = MagicMock()
        mock_weather_instance.get_current_weather.return_value = {
            'temperature': 30.0,
            'humidity': 55.0,
            'rainfall': 0.0,
            'wind_speed': 4.0
        }
        mock_weather_service.return_value = mock_weather_instance

        service = IrrigationPredictionService()
        service.model = mock_model

        schedule = service.generate_irrigation_schedule(self.field, self.user)

        self.assertEqual(schedule.field, self.field)
        self.assertEqual(schedule.user, self.user)
        self.assertEqual(schedule.predicted_water_amount, Decimal('25.0'))
        self.assertEqual(schedule.confidence_score, 0.7)
        self.assertEqual(schedule.status, 'pending')
        self.assertIn('soil moisture', schedule.irrigation_reason.lower())


class SerializerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.field = Field.objects.create(
            user=self.user,
            name='Test Field',
            crop_type='Maize',
            soil_type='Loam',
            region='central',
            current_season='Dry',
            area=1.0,
            latitude=-15.3875,
            longitude=28.3228,
            current_soil_moisture=35,
            planting_date=date.today() - timedelta(days=45)
        )

    def test_schedule_serializer(self):
        schedule = IrrigationSchedule.objects.create(
            field=self.field,
            user=self.user,
            predicted_water_amount=25.0,
            confidence_score=0.8,
            irrigation_reason='Test irrigation',
            recommended_date=date.today() + timedelta(days=1),
            recommended_time=time(6, 0),
            priority_level='medium'
        )

        serializer = IrrigationScheduleSerializer(schedule)
        data = serializer.data

        self.assertEqual(data['field'], self.field.id)
        self.assertEqual(data['field_name'], self.field.name)
        self.assertEqual(data['predicted_water_amount'], '25.00')
        self.assertEqual(data['status'], 'pending')

    def test_history_serializer(self):
        history = IrrigationHistory.objects.create(
            field=self.field,
            user=self.user,
            water_amount_used=22.5,
            irrigation_method='drip',
            irrigation_date=date.today(),
            irrigation_time=time(6, 30),
            duration_minutes=45
        )

        serializer = IrrigationHistorySerializer(history)
        data = serializer.data

        self.assertEqual(data['field'], self.field.id)
        self.assertEqual(data['field_name'], self.field.name)
        self.assertEqual(data['water_amount_used'], '22.50')
        self.assertEqual(data['irrigation_method'], 'drip')
