import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from exercises.models import Exercise, TestCase
from skills.models import Skill

User = get_user_model()

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='AdminPassword123!',
        full_name='Admin User'
    )

@pytest.fixture
def student_user():
    return User.objects.create_user(
        username='student',
        email='student@example.com',
        password='StudentPassword123!',
        full_name='Student User'
    )

@pytest.fixture
def skill():
    return Skill.objects.create(name='Python Basics', category='Language')

@pytest.fixture
def exercise(admin_user):
    return Exercise.objects.create(
        stable_id='ex-01',
        title='Hello World',
        statement='Print Hello World',
        status=Exercise.Status.PUBLISHED,
        author=admin_user
    )

@pytest.fixture
def draft_exercise(admin_user):
    return Exercise.objects.create(
        stable_id='ex-02',
        title='Draft Exercise',
        statement='Draft',
        status=Exercise.Status.DRAFT,
        author=admin_user
    )

@pytest.fixture
def test_case(exercise):
    return TestCase.objects.create(
        exercise=exercise,
        inputs='',
        expected_outputs='Hello World\n',
        case_type=TestCase.Type.VISIBLE
    )

@pytest.fixture
def hidden_test_case(exercise):
    return TestCase.objects.create(
        exercise=exercise,
        inputs='hidden',
        expected_outputs='hidden_output',
        case_type=TestCase.Type.HIDDEN
    )

@pytest.mark.django_db
class TestExercises:
    def test_list_exercises_student(self, api_client, student_user, exercise, draft_exercise):
        api_client.force_authenticate(user=student_user)
        url = reverse('exercise_list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Should only see published
        assert len(response.data) == 1
        assert response.data[0]['stable_id'] == exercise.stable_id

    def test_list_exercises_admin(self, api_client, admin_user, exercise, draft_exercise):
        api_client.force_authenticate(user=admin_user)
        url = reverse('exercise_list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Should see both
        assert len(response.data) == 2

    def test_exercise_detail_visible_testcases(self, api_client, student_user, exercise, test_case, hidden_test_case):
        api_client.force_authenticate(user=student_user)
        url = reverse('exercise_detail', kwargs={'stable_id': exercise.stable_id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Only visible test cases should be returned
        assert len(response.data['test_cases']) == 1
        assert response.data['test_cases'][0]['case_type'] == 'VISIBLE'

    def test_admin_create_exercise(self, api_client, admin_user, skill):
        api_client.force_authenticate(user=admin_user)
        url = reverse('exercise_admin_create')
        data = {
            'stable_id': 'ex-03',
            'title': 'New Ex',
            'statement': 'Solve this',
            'status': 'PUBLISHED',
            'skill_ids': [skill.id],
            'test_cases': [
                {'inputs': '1', 'expected_outputs': '1', 'case_type': 'VISIBLE'}
            ]
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Exercise.objects.filter(stable_id='ex-03').exists()
        
    def test_student_cannot_create_exercise(self, api_client, student_user):
        api_client.force_authenticate(user=student_user)
        url = reverse('exercise_admin_create')
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_update_exercise(self, api_client, admin_user, exercise):
        api_client.force_authenticate(user=admin_user)
        url = reverse('exercise_admin_update', kwargs={'stable_id': exercise.stable_id})
        data = {
            'stable_id': exercise.stable_id,
            'title': 'Updated Title',
            'statement': exercise.statement
        }
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        exercise.refresh_from_db()
        assert exercise.title == 'Updated Title'

    def test_admin_soft_delete(self, api_client, admin_user, exercise):
        api_client.force_authenticate(user=admin_user)
        url = reverse('exercise_admin_update', kwargs={'stable_id': exercise.stable_id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        exercise.refresh_from_db()
        assert exercise.is_deleted == True
