from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import UserPreferences

User = get_user_model()


class UserPreferencesModelTest(TestCase):
    """Test cases for UserPreferences model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_preferences_creation(self):
        """Test that preferences are created with defaults."""
        preferences = UserPreferences.objects.create(user=self.user)

        self.assertEqual(preferences.user, self.user)
        self.assertTrue(preferences.email_notifications)
        self.assertEqual(preferences.temperature_unit, 'celsius')
        self.assertEqual(preferences.volume_unit, 'liters')
        self.assertEqual(preferences.default_irrigation_duration, 30)

    def test_preferences_str(self):
        """Test string representation of preferences."""
        preferences = UserPreferences.objects.create(user=self.user)
        self.assertEqual(str(preferences), "test@example.com's preferences")


class UserPreferencesAPITestCase(APITestCase):
    """Test cases for user preferences API."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_get_preferences_creates_default(self):
        """Test that GET creates default preferences if none exist."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/settings/preferences/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertTrue(data['email_notifications'])
        self.assertEqual(data['temperature_unit'], 'celsius')
        self.assertEqual(data['volume_unit'], 'liters')

        # Check that preferences were created in database
        preferences = UserPreferences.objects.get(user=self.user)
        self.assertIsNotNone(preferences)

    def test_update_preferences(self):
        """Test updating user preferences."""
        self.client.force_authenticate(user=self.user)

        update_data = {
            'email_notifications': False,
            'temperature_unit': 'fahrenheit',
            'volume_unit': 'gallons',
            'default_irrigation_duration': 45
        }

        response = self.client.patch('/api/settings/preferences/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertFalse(data['email_notifications'])
        self.assertEqual(data['temperature_unit'], 'fahrenheit')
        self.assertEqual(data['volume_unit'], 'gallons')
        self.assertEqual(data['default_irrigation_duration'], 45)

    def test_reset_preferences(self):
        """Test resetting preferences to defaults."""
        self.client.force_authenticate(user=self.user)

        # First update some preferences
        self.client.patch('/api/settings/preferences/', {
            'email_notifications': False,
            'temperature_unit': 'fahrenheit'
        }, format='json')

        # Then reset
        response = self.client.post('/api/settings/preferences/reset/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertTrue(data['email_notifications'])
        self.assertEqual(data['temperature_unit'], 'celsius')

    def test_unauthenticated_access(self):
        """Test that unauthenticated users can't access preferences."""
        response = self.client.get('/api/settings/preferences/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
