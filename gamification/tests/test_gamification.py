import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from gamification.models import Achievement, UserGamificationProfile, Challenge
from gamification.services import award_points, award_achievement

User = get_user_model()

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='gamer',
        email='gamer@example.com',
        password='TestPassword123!',
        full_name='Gamer User'
    )

@pytest.fixture
def other_user():
    return User.objects.create_user(
        username='other_gamer',
        email='other@example.com',
        password='TestPassword123!',
        full_name='Other Gamer'
    )

@pytest.fixture
def achievement():
    return Achievement.objects.create(
        stable_id='first_blood',
        title='First Blood',
        description='Solve your first exercise.'
    )

@pytest.fixture
def active_challenge():
    return Challenge.objects.create(
        stable_id='weekly-1',
        title='Weekly Challenge 1',
        description='Solve arrays',
        start_date=timezone.now() - timedelta(days=1),
        end_date=timezone.now() + timedelta(days=5)
    )

@pytest.fixture
def past_challenge():
    return Challenge.objects.create(
        stable_id='weekly-0',
        title='Weekly Challenge 0',
        description='Past',
        start_date=timezone.now() - timedelta(days=10),
        end_date=timezone.now() - timedelta(days=5)
    )

@pytest.mark.django_db
class TestGamification:
    def test_award_points_idempotency(self, user):
        success1, msg1 = award_points(user, 'EXERCISE_SOLVED', 10, 'Solved ex-1', 'solve_ex_1')
        assert success1 is True
        
        # Test idempotency
        success2, msg2 = award_points(user, 'EXERCISE_SOLVED', 10, 'Solved ex-1', 'solve_ex_1')
        assert success2 is False
        
        profile = UserGamificationProfile.objects.get(user=user)
        assert profile.points == 10
        assert profile.level == 1 # (10 // 100) + 1

    def test_award_achievement_idempotency(self, user, achievement):
        success1, msg1 = award_achievement(user, achievement.stable_id, 'Solved first')
        assert success1 is True
        
        # Test idempotency
        success2, msg2 = award_achievement(user, achievement.stable_id, 'Solved first')
        assert success2 is False
        
        assert user.achievements.count() == 1

    def test_get_profile(self, api_client, user):
        api_client.force_authenticate(user=user)
        award_points(user, 'DAILY_LOGIN', 150, 'Login', 'login_1')
        
        url = reverse('gamification_profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['points'] == 150
        assert response.data['level'] == 2
        assert response.data['username'] == user.username

    def test_get_ranking(self, api_client, user, other_user):
        api_client.force_authenticate(user=user)
        award_points(other_user, 'EXERCISE_SOLVED', 500, 'Solve', 'solve_other')
        award_points(user, 'EXERCISE_SOLVED', 200, 'Solve', 'solve_user')
        
        url = reverse('gamification_ranking')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        # other_user should be first
        assert response.data[0]['username'] == other_user.username
        assert response.data[1]['username'] == user.username

    def test_list_active_challenges(self, api_client, user, active_challenge, past_challenge):
        api_client.force_authenticate(user=user)
        url = reverse('gamification_challenges')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['stable_id'] == active_challenge.stable_id

    def test_join_active_challenge(self, api_client, user, active_challenge):
        api_client.force_authenticate(user=user)
        url = reverse('gamification_join_challenge')
        response = api_client.post(url, {'challenge_id': active_challenge.stable_id})
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Cannot join twice
        response2 = api_client.post(url, {'challenge_id': active_challenge.stable_id})
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_join_past_challenge_fails(self, api_client, user, past_challenge):
        api_client.force_authenticate(user=user)
        url = reverse('gamification_join_challenge')
        response = api_client.post(url, {'challenge_id': past_challenge.stable_id})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
