import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPassword123!',
        full_name='Test User'
    )

@pytest.mark.django_db
class TestAccounts:
    def test_register_user(self, api_client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePassword123!',
            'full_name': 'New User'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'password' not in response.data
        assert response.data['username'] == 'newuser'
        
        # Verify user was created
        assert User.objects.filter(username='newuser').exists()

    def test_register_duplicate_username(self, api_client, user):
        url = reverse('register')
        data = {
            'username': user.username,
            'email': 'other@example.com',
            'password': 'SecurePassword123!',
            'full_name': 'Other User'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

    def test_login_with_username(self, api_client, user):
        url = reverse('login')
        data = {
            'username': user.username,
            'password': 'TestPassword123!'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_with_email(self, api_client, user):
        url = reverse('login')
        data = {
            'email': user.email,
            'password': 'TestPassword123!'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_invalid_credentials(self, api_client, user):
        url = reverse('login')
        data = {
            'username': user.username,
            'password': 'WrongPassword!'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data

    def test_login_enumeration_protection(self, api_client):
        url = reverse('login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_view(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email

    def test_logout(self, api_client, user):
        refresh = RefreshToken.for_user(user)
        api_client.force_authenticate(user=user)
        url = reverse('logout')
        response = api_client.post(url, {'refresh': str(refresh)})
        assert response.status_code == status.HTTP_205_RESET_CONTENT
        
        # Verify token is blacklisted by trying to use it
        url_refresh = reverse('token_refresh')
        response_refresh = api_client.post(url_refresh, {'refresh': str(refresh)})
        assert response_refresh.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('change_password')
        data = {
            'old_password': 'TestPassword123!',
            'new_password': 'NewSecurePassword123!'
        }
        response = api_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify password changed
        user.refresh_from_db()
        assert user.check_password('NewSecurePassword123!')

    def test_role_authorization(self, api_client):
        # Additional checks to ensure user created has STUDENT role by default
        user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='TestPassword123!',
            full_name='Student'
        )
        assert user.role == User.Role.STUDENT
