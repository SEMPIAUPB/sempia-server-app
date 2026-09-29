import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from exercises.models import Exercise
from submissions.models import Submission

User = get_user_model()

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def student_user():
    return User.objects.create_user(
        username='student',
        email='student@example.com',
        password='StudentPassword123!',
        full_name='Student User'
    )

@pytest.fixture
def other_student():
    return User.objects.create_user(
        username='other',
        email='other@example.com',
        password='StudentPassword123!',
        full_name='Other Student'
    )

@pytest.fixture
def exercise(student_user):
    return Exercise.objects.create(
        stable_id='ex-01',
        title='Hello World',
        statement='Print Hello World',
        status=Exercise.Status.PUBLISHED,
        author=student_user
    )

@pytest.fixture
def draft_exercise(student_user):
    return Exercise.objects.create(
        stable_id='ex-02',
        title='Draft',
        statement='Draft',
        status=Exercise.Status.DRAFT,
        author=student_user
    )

@pytest.mark.django_db
class TestSubmissions:
    def test_submit_code_to_published(self, api_client, student_user, exercise):
        api_client.force_authenticate(user=student_user)
        url = reverse('submission_list_create')
        data = {
            'exercise_id': exercise.stable_id,
            'source_code': 'print("Hello World")',
            'language': 'python'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['state'] == 'PENDING'
        
        # Verify in DB
        sub = Submission.objects.get(id=response.data['id'])
        assert sub.state == Submission.State.PENDING
        assert sub.author == student_user

    def test_submit_code_to_draft_fails(self, api_client, student_user, draft_exercise):
        api_client.force_authenticate(user=student_user)
        url = reverse('submission_list_create')
        data = {
            'exercise_id': draft_exercise.stable_id,
            'source_code': 'print("Draft")',
            'language': 'python'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_submissions_only_owns(self, api_client, student_user, other_student, exercise):
        Submission.objects.create(author=student_user, exercise=exercise, source_code='1', language='python')
        Submission.objects.create(author=other_student, exercise=exercise, source_code='2', language='python')
        
        api_client.force_authenticate(user=student_user)
        url = reverse('submission_list_create')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['author_username'] == student_user.username
