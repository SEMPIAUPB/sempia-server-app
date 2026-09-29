from django.db import models
from django.conf import settings
from exercises.models import Exercise

User = settings.AUTH_USER_MODEL

class UserGamificationProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gamification_profile')
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    current_streak = models.IntegerField(default=0)
    highest_streak = models.IntegerField(default=0)
    last_action_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - Lvl {self.level} ({self.points} pts)"

class ExperienceEvent(models.Model):
    class EventType(models.TextChoices):
        EXERCISE_SOLVED = 'EXERCISE_SOLVED', 'Exercise Solved'
        CHALLENGE_WON = 'CHALLENGE_WON', 'Challenge Won'
        DAILY_LOGIN = 'DAILY_LOGIN', 'Daily Login'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experience_events')
    event_type = models.CharField(max_length=50, choices=EventType.choices)
    points_awarded = models.IntegerField()
    description = models.CharField(max_length=255)
    reference_id = models.CharField(max_length=255, unique=True, help_text="Used for idempotency (e.g. 'solve_ex_42')")
    created_at = models.DateTimeField(auto_now_add=True)

class Achievement(models.Model):
    stable_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.title

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f"{self.user} - {self.achievement.title}"

class Challenge(models.Model):
    stable_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    exercises = models.ManyToManyField(Exercise, related_name='challenges')

    def __str__(self):
        return self.title

class ChallengeParticipation(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participations')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('challenge', 'user')
