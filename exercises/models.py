from django.db import models
from django.conf import settings
from skills.models import Skill

class Exercise(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        ARCHIVED = 'ARCHIVED', 'Archived'

    stable_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    statement = models.TextField()
    difficulty = models.IntegerField(default=100)
    time_limit_ms = models.IntegerField(default=1000)
    memory_limit_kb = models.IntegerField(default=256000)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='authored_exercises')
    skills = models.ManyToManyField(Skill, through='ExerciseSkill', related_name='exercises')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.stable_id} - {self.title}"

class ExerciseSkill(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('exercise', 'skill')

class TestCase(models.Model):
    class Type(models.TextChoices):
        VISIBLE = 'VISIBLE', 'Visible'
        HIDDEN = 'HIDDEN', 'Hidden'

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='test_cases')
    inputs = models.TextField()
    expected_outputs = models.TextField()
    case_type = models.CharField(max_length=20, choices=Type.choices, default=Type.HIDDEN)
    
    def __str__(self):
        return f"{self.exercise.stable_id} - {self.case_type}"
