from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, timedelta
from decimal import Decimal
from .models import Field

User = get_user_model()


class FieldModelTestCase(TestCase):
    """Test cases for Field model."""
    
    def setUp(self):
        """Set up test user and field data."""
        self.user = User.objects.create_user(
            email='farmer@test.com',
            name='Test Farmer',
            password='testpass123'
        )
        
        self.valid_field_data = {
            'user': self.user,
            'name': 'Test Field',
            'location': 'Chilanga, Lusaka',
            'region': 'lusaka',
            'area': Decimal('2.50'),
            'crop_type': 'Maize',
            'planting_date': date.today() - timedelta(days=30),
            'soil_type': 'Loam',
            'current_soil_moisture': 50,
            'irrigation_method': 'drip',
            'current_season': 'Wet',
        }
    
    def test_create_field_with_valid_data(self):
        """Test creating a field with valid data."""
        field = Field.objects.create(**self.valid_field_data)
        
        self.assertEqual(field.name, 'Test Field')
        self.assertEqual(field.user, self.user)
        self.assertEqual(field.crop_type, 'Maize')
        self.assertEqual(field.region, 'lusaka')
        self.assertTrue(field.is_active)
        self.assertIsNotNone(field.created_at)
        self.assertIsNotNone(field.updated_at)
    
    def test_field_string_representation(self):
        """Test __str__ method of Field model."""
        field = Field.objects.create(**self.valid_field_data)
        expected = f"Test Field (Maize) - {self.user.email}"
        self.assertEqual(str(field), expected)
    
    def test_crop_days_property(self):
        """Test crop_days property calculation."""
        field = Field.objects.create(**self.valid_field_data)
        expected_days = (date.today() - field.planting_date).days
        self.assertEqual(field.crop_days, expected_days)
    
    def test_crop_age_weeks_property(self):
        """Test crop_age_weeks property calculation."""
        field = Field.objects.create(**self.valid_field_data)
        expected_weeks = field.crop_days // 7
        self.assertEqual(field.crop_age_weeks, expected_weeks)
    
    def test_update_soil_moisture_valid(self):
        """Test updating soil moisture with valid value."""
        field = Field.objects.create(**self.valid_field_data)
        result = field.update_soil_moisture(75)
        
        self.assertTrue(result)
        field.refresh_from_db()
        self.assertEqual(field.current_soil_moisture, 75)
    
    def test_update_soil_moisture_invalid_too_low(self):
        """Test updating soil moisture with value below 0."""
        field = Field.objects.create(**self.valid_field_data)
        result = field.update_soil_moisture(-10)
        
        self.assertFalse(result)
        field.refresh_from_db()
        self.assertEqual(field.current_soil_moisture, 50)  # Unchanged
    
    def test_update_soil_moisture_invalid_too_high(self):
        """Test updating soil moisture with value above 100."""
        field = Field.objects.create(**self.valid_field_data)
        result = field.update_soil_moisture(150)
        
        self.assertFalse(result)
        field.refresh_from_db()
        self.assertEqual(field.current_soil_moisture, 50)  # Unchanged
    
    def test_get_ai_model_input(self):
        """Test get_ai_model_input method."""
        field = Field.objects.create(**self.valid_field_data)
        
        weather_data = {
            'temperature': 28.0,
            'humidity': 55.0,
            'rainfall': 0.0,
            'windspeed': 12.0,
        }
        
        ai_input = field.get_ai_model_input(weather_data)
        
        # Verify all 10 features are present
        self.assertEqual(len(ai_input), 10)
        
        # Verify field-based features
        self.assertEqual(ai_input['CropType'], 'Maize')
        self.assertEqual(ai_input['SoilMoisture'], 50)
        self.assertEqual(ai_input['soilType'], 'Loam')
        self.assertEqual(ai_input['region'], 'Lusaka')
        self.assertEqual(ai_input['season'], 'Wet')
        
        # Verify weather features
        self.assertEqual(ai_input['temperature'], 28.0)
        self.assertEqual(ai_input['humidity'], 55.0)
        self.assertEqual(ai_input['rainfall'], 0.0)
        self.assertEqual(ai_input['windspeed'], 12.0)
        
        # Verify crop days
        self.assertIsInstance(ai_input['CropDays'], int)
        self.assertGreater(ai_input['CropDays'], 0)
    
    def test_field_cascade_delete_on_user_delete(self):
        """Test that fields are deleted when user is deleted."""
        field = Field.objects.create(**self.valid_field_data)
        field_id = field.id
        
        self.user.delete()
        
        with self.assertRaises(Field.DoesNotExist):
            Field.objects.get(id=field_id)
    
    def test_multiple_fields_per_user(self):
        """Test that a user can have multiple fields."""
        field1 = Field.objects.create(**self.valid_field_data)
        
        field2_data = self.valid_field_data.copy()
        field2_data['name'] = 'Second Field'
        field2_data['crop_type'] = 'Wheat'
        field2 = Field.objects.create(**field2_data)
        
        user_fields = Field.objects.filter(user=self.user)
        self.assertEqual(user_fields.count(), 2)
        self.assertIn(field1, user_fields)
        self.assertIn(field2, user_fields)


class FieldAPITestCase(APITestCase):
    """Test cases for Field API endpoints."""
    
    def setUp(self):
        """Set up test users and authentication."""
        self.user1 = User.objects.create_user(
            email='farmer1@test.com',
            name='Farmer One',
            password='testpass123',
            location='Lusaka'
        )
        
        self.user2 = User.objects.create_user(
            email='farmer2@test.com',
            name='Farmer Two',
            password='testpass123',
            location='Central Province'
        )
        
        self.client = APIClient()
        
        self.valid_field_data = {
            'name': 'Test Field',
            'location': 'Chilanga, Lusaka',
            'region': 'lusaka',
            'area': 2.50,
            'crop_type': 'Maize',
            'planting_date': (date.today() - timedelta(days=30)).isoformat(),
            'soil_type': 'Loam',
            'current_soil_moisture': 50,
            'irrigation_method': 'drip',
            'current_season': 'Wet',
            'notes': 'Test notes',
            'is_active': True,
        }
    
    def _login_user(self, user):
        """Helper method to login a user and get token."""
        response = self.client.post('/api/auth/login/', {
            'email': user.email,
            'password': 'testpass123'
        }, format='json')
        
        # Check if login was successful
        if response.status_code != status.HTTP_200_OK:
            raise Exception(f"Login failed with status {response.status_code}: {response.data}")
        
        if 'access' not in response.data:
            raise Exception(f"No access token in response: {response.data}")
        
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return token
    
    def test_create_field_authenticated(self):
        """Test creating a field with authentication."""
        self._login_user(self.user1)
        
        response = self.client.post('/api/fields/', self.valid_field_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Field')
        self.assertEqual(response.data['user_email'], self.user1.email)
        self.assertEqual(response.data['crop_type'], 'Maize')
        
        # Verify field exists in database
        self.assertTrue(Field.objects.filter(name='Test Field', user=self.user1).exists())
    
    def test_create_field_unauthenticated(self):
        """Test creating a field without authentication fails."""
        response = self.client.post('/api/fields/', self.valid_field_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Field.objects.count(), 0)
    
    def test_create_field_with_invalid_area(self):
        """Test creating a field with invalid area."""
        self._login_user(self.user1)
        
        invalid_data = self.valid_field_data.copy()
        invalid_data['area'] = -1
        
        response = self.client.post('/api/fields/', invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('area', response.data)
    
    def test_create_field_with_invalid_soil_moisture(self):
        """Test creating a field with invalid soil moisture."""
        self._login_user(self.user1)
        
        invalid_data = self.valid_field_data.copy()
        invalid_data['current_soil_moisture'] = 150
        
        response = self.client.post('/api/fields/', invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('current_soil_moisture', response.data)
    
    def test_create_field_with_future_planting_date(self):
        """Test creating a field with future planting date."""
        self._login_user(self.user1)
        
        invalid_data = self.valid_field_data.copy()
        invalid_data['planting_date'] = (date.today() + timedelta(days=10)).isoformat()
        
        response = self.client.post('/api/fields/', invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('planting_date', response.data)
    
    def test_list_fields_only_own_fields(self):
        """Test that users only see their own fields."""
        self._login_user(self.user1)
        
        # Create fields for user1
        Field.objects.create(user=self.user1, name='User1 Field 1', region='lusaka',
                            area=2.5, crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                            soil_type='Loam')
        Field.objects.create(user=self.user1, name='User1 Field 2', region='central',
                            area=3.0, crop_type='Wheat', planting_date=date.today() - timedelta(days=20),
                            soil_type='Clay')
        
        # Create field for user2
        Field.objects.create(user=self.user2, name='User2 Field', region='southern',
                            area=1.5, crop_type='Rice', planting_date=date.today() - timedelta(days=40),
                            soil_type='Sandy')
        
        response = self.client.get('/api/fields/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only user1's fields
        
        field_names = [field['name'] for field in response.data]
        self.assertIn('User1 Field 1', field_names)
        self.assertIn('User1 Field 2', field_names)
        self.assertNotIn('User2 Field', field_names)
    
    def test_retrieve_field_detail(self):
        """Test retrieving a single field's details."""
        self._login_user(self.user1)
        
        field = Field.objects.create(user=self.user1, name='Detail Field', region='lusaka',
                                     area=2.5, crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                                     soil_type='Loam')
        
        response = self.client.get(f'/api/fields/{field.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Detail Field')
        self.assertEqual(response.data['id'], field.id)
    
    def test_retrieve_other_users_field_fails(self):
        """Test that users cannot access other users' fields."""
        self._login_user(self.user1)
        
        # Create field for user2
        field = Field.objects.create(user=self.user2, name='User2 Field', region='lusaka',
                                     area=2.5, crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                                     soil_type='Loam')
        
        response = self.client.get(f'/api/fields/{field.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_field(self):
        """Test updating a field."""
        self._login_user(self.user1)
        
        field = Field.objects.create(user=self.user1, name='Original Name', region='lusaka',
                                     area=2.5, crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                                     soil_type='Loam')
        
        update_data = {
            'name': 'Updated Name',
            'current_soil_moisture': 65,
            'notes': 'Updated notes'
        }
        
        response = self.client.patch(f'/api/fields/{field.id}/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')
        self.assertEqual(response.data['current_soil_moisture'], 65)
        
        # Verify database update
        field.refresh_from_db()
        self.assertEqual(field.name, 'Updated Name')
        self.assertEqual(field.current_soil_moisture, 65)
    
    def test_update_other_users_field_fails(self):
        """Test that users cannot update other users' fields."""
        self._login_user(self.user1)
        
        field = Field.objects.create(user=self.user2, name='User2 Field', region='lusaka',
                                     area=2.5, crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                                     soil_type='Loam')
        
        update_data = {'name': 'Hacked Name'}
        response = self.client.patch(f'/api/fields/{field.id}/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify field unchanged
        field.refresh_from_db()
        self.assertEqual(field.name, 'User2 Field')
    
    def test_delete_field(self):
        """Test deleting a field."""
        self._login_user(self.user1)
        
        field = Field.objects.create(user=self.user1, name='Delete Me', region='lusaka',
                                     area=2.5, crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                                     soil_type='Loam')
        field_id = field.id
        
        response = self.client.delete(f'/api/fields/{field_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify field deleted from database
        self.assertFalse(Field.objects.filter(id=field_id).exists())
    
    def test_delete_other_users_field_fails(self):
        """Test that users cannot delete other users' fields."""
        self._login_user(self.user1)
        
        field = Field.objects.create(user=self.user2, name='User2 Field', region='lusaka',
                                     area=2.5, crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                                     soil_type='Loam')
        field_id = field.id
        
        response = self.client.delete(f'/api/fields/{field_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify field still exists
        self.assertTrue(Field.objects.filter(id=field_id).exists())
    
    def test_update_moisture_endpoint(self):
        """Test the update moisture custom endpoint."""
        self._login_user(self.user1)
        
        field = Field.objects.create(user=self.user1, name='Moisture Test', region='lusaka',
                                     area=2.5, crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                                     soil_type='Loam', current_soil_moisture=50)
        
        response = self.client.patch(
            f'/api/fields/{field.id}/update-moisture/',
            {'current_soil_moisture': 35},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_soil_moisture'], 35)
        
        # Verify database update
        field.refresh_from_db()
        self.assertEqual(field.current_soil_moisture, 35)
    
    def test_get_ai_input_endpoint(self):
        """Test the AI input custom endpoint."""
        self._login_user(self.user1)
        
        field = Field.objects.create(user=self.user1, name='AI Test', region='lusaka',
                                     area=2.5, crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                                     soil_type='Loam', current_soil_moisture=50, current_season='Wet')
        
        response = self.client.get(
            f'/api/fields/{field.id}/ai-input/',
            {'temperature': 28, 'humidity': 55, 'rainfall': 0, 'windspeed': 12}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ai_model_input', response.data)
        
        ai_input = response.data['ai_model_input']
        self.assertEqual(ai_input['CropType'], 'Maize')
        self.assertEqual(ai_input['soilType'], 'Loam')
        self.assertEqual(ai_input['temperature'], 28.0)
        self.assertEqual(ai_input['humidity'], 55.0)
    
    def test_get_statistics_endpoint(self):
        """Test the statistics custom endpoint."""
        self._login_user(self.user1)
        
        # Create multiple fields for user1
        Field.objects.create(user=self.user1, name='Field 1', region='lusaka', area=2.5,
                            crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                            soil_type='Loam', is_active=True)
        Field.objects.create(user=self.user1, name='Field 2', region='central', area=3.0,
                            crop_type='Maize', planting_date=date.today() - timedelta(days=20),
                            soil_type='Clay', is_active=True)
        Field.objects.create(user=self.user1, name='Field 3', region='lusaka', area=1.5,
                            crop_type='Wheat', planting_date=date.today() - timedelta(days=40),
                            soil_type='Sandy', is_active=False)
        
        response = self.client.get('/api/fields/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_fields'], 3)
        self.assertEqual(response.data['active_fields'], 2)
        self.assertEqual(response.data['inactive_fields'], 1)
        self.assertEqual(response.data['total_area_hectares'], 7.0)
        
        # Check crop distribution
        self.assertEqual(response.data['crop_distribution']['Maize'], 2)
        self.assertEqual(response.data['crop_distribution']['Wheat'], 1)
        
        # Check region distribution
        self.assertEqual(response.data['region_distribution']['Lusaka'], 2)
        self.assertEqual(response.data['region_distribution']['Central Province'], 1)
    
    def test_filter_fields_by_crop_type(self):
        """Test filtering fields by crop type."""
        self._login_user(self.user1)
        
        Field.objects.create(user=self.user1, name='Maize Field', region='lusaka', area=2.5,
                            crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                            soil_type='Loam')
        Field.objects.create(user=self.user1, name='Wheat Field', region='central', area=3.0,
                            crop_type='Wheat', planting_date=date.today() - timedelta(days=20),
                            soil_type='Clay')
        
        response = self.client.get('/api/fields/', {'crop_type': 'Maize'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['crop_type'], 'Maize')
    
    def test_filter_fields_by_region(self):
        """Test filtering fields by region."""
        self._login_user(self.user1)
        
        Field.objects.create(user=self.user1, name='Lusaka Field', region='lusaka', area=2.5,
                            crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                            soil_type='Loam')
        Field.objects.create(user=self.user1, name='Central Field', region='central', area=3.0,
                            crop_type='Wheat', planting_date=date.today() - timedelta(days=20),
                            soil_type='Clay')
        
        response = self.client.get('/api/fields/', {'region': 'central'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['region'], 'central')
    
    def test_search_fields_by_name(self):
        """Test searching fields by name."""
        self._login_user(self.user1)
        
        Field.objects.create(user=self.user1, name='North Field', region='lusaka', area=2.5,
                            crop_type='Maize', planting_date=date.today() - timedelta(days=30),
                            soil_type='Loam')
        Field.objects.create(user=self.user1, name='South Field', region='central', area=3.0,
                            crop_type='Wheat', planting_date=date.today() - timedelta(days=20),
                            soil_type='Clay')
        
        response = self.client.get('/api/fields/', {'search': 'North'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'North Field')
