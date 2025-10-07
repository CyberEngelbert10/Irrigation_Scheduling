import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'email': 'test@example.com',
        'name': 'Test User',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!',
        'location': 'Nairobi'
    }


@pytest.mark.django_db
class TestRegistration:
    
    def test_register_user_success(self, api_client, user_data):
        """Test successful user registration."""
        response = api_client.post('/api/auth/register/', user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['email'] == user_data['email']
        assert User.objects.filter(email=user_data['email']).exists()
    
    def test_register_duplicate_email(self, api_client, user_data):
        """Test registration with duplicate email fails."""
        api_client.post('/api/auth/register/', user_data)
        response = api_client.post('/api/auth/register/', user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_password_mismatch(self, api_client, user_data):
        """Test registration fails when passwords don't match."""
        user_data['password_confirm'] = 'DifferentPass123!'
        response = api_client.post('/api/auth/register/', user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_weak_password(self, api_client, user_data):
        """Test registration fails with weak password."""
        user_data['password'] = '123'
        user_data['password_confirm'] = '123'
        response = api_client.post('/api/auth/register/', user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:
    
    def test_login_success(self, api_client, user_data):
        """Test successful login returns JWT tokens."""
        # Register user first
        api_client.post('/api/auth/register/', user_data)
        
        # Login
        response = api_client.post('/api/auth/login/', {
            'email': user_data['email'],
            'password': user_data['password']
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_wrong_password(self, api_client, user_data):
        """Test login fails with wrong password."""
        api_client.post('/api/auth/register/', user_data)
        
        response = api_client.post('/api/auth/login/', {
            'email': user_data['email'],
            'password': 'WrongPass123!'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, api_client):
        """Test login fails for nonexistent user."""
        response = api_client.post('/api/auth/login/', {
            'email': 'nonexistent@example.com',
            'password': 'SomePass123!'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserDetail:
    
    def test_get_user_authenticated(self, api_client, user_data):
        """Test authenticated user can retrieve their details."""
        # Register and login
        api_client.post('/api/auth/register/', user_data)
        login_response = api_client.post('/api/auth/login/', {
            'email': user_data['email'],
            'password': user_data['password']
        })
        token = login_response.data['access']
        
        # Get user details
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.get('/api/auth/user/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user_data['email']
        assert response.data['name'] == user_data['name']
    
    def test_get_user_unauthenticated(self, api_client):
        """Test unauthenticated request fails."""
        response = api_client.get('/api/auth/user/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_user_profile(self, api_client, user_data):
        """Test user can update their profile."""
        # Register and login
        api_client.post('/api/auth/register/', user_data)
        login_response = api_client.post('/api/auth/login/', {
            'email': user_data['email'],
            'password': user_data['password']
        })
        token = login_response.data['access']
        
        # Update profile
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.patch('/api/auth/user/', {
            'name': 'Updated Name',
            'location': 'Mombasa'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Name'
        assert response.data['location'] == 'Mombasa'


@pytest.mark.django_db
class TestChangePassword:
    
    def test_change_password_success(self, api_client, user_data):
        """Test successful password change."""
        # Register and login
        api_client.post('/api/auth/register/', user_data)
        login_response = api_client.post('/api/auth/login/', {
            'email': user_data['email'],
            'password': user_data['password']
        })
        token = login_response.data['access']
        
        # Change password
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.post('/api/auth/change-password/', {
            'old_password': user_data['password'],
            'new_password': 'NewPass123!',
            'new_password_confirm': 'NewPass123!'
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify new password works
        login_response = api_client.post('/api/auth/login/', {
            'email': user_data['email'],
            'password': 'NewPass123!'
        })
        assert login_response.status_code == status.HTTP_200_OK
    
    def test_change_password_wrong_old_password(self, api_client, user_data):
        """Test password change fails with wrong old password."""
        api_client.post('/api/auth/register/', user_data)
        login_response = api_client.post('/api/auth/login/', {
            'email': user_data['email'],
            'password': user_data['password']
        })
        token = login_response.data['access']
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.post('/api/auth/change-password/', {
            'old_password': 'WrongPass123!',
            'new_password': 'NewPass123!',
            'new_password_confirm': 'NewPass123!'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
