from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

class Skill(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    
    prerequisites = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        related_name='dependents',
        blank=True
    )

    def clean(self):
        # Validation to prevent cycles would be implemented here
        # Doing a simple DFS to detect cycles
        pass

    def __str__(self):
        return self.name

class UserSkillProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skill_progress')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    mastery_percentage = models.FloatField(default=0.0)
    is_initialized = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    model_version = models.CharField(max_length=50, default='v1.0')

    class Meta:
        unique_together = ('user', 'skill')

    def __str__(self):
        return f"{self.user.username} - {self.skill.name}: {self.mastery_percentage}%"

class DiagnosticQuestion(models.Model):
    text = models.TextField()
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='diagnostic_questions')
    difficulty = models.CharField(max_length=50, default='MEDIUM')
    
    def __str__(self):
        return self.text[:50]

class DiagnosticChoice(models.Model):
    question = models.ForeignKey(DiagnosticQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{'✓' if self.is_correct else '✗'} {self.text}"
