from rest_framework import serializers
from django.utils import timezone
from .models import UserGamificationProfile, Achievement, UserAchievement, Challenge, ChallengeParticipation
from django.contrib.auth import get_user_model
from exercises.models import Exercise
from submissions.models import Submission

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = UserGamificationProfile
        fields = ['id', 'username', 'full_name', 'points', 'level', 'current_streak', 'highest_streak']

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'stable_id', 'title', 'description', 'image_url']

class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'awarded_at', 'reason']

class ChallengeExerciseSerializer(serializers.ModelSerializer):
    is_solved = serializers.SerializerMethodField()
    description = serializers.CharField(source='statement', read_only=True)

    class Meta:
        model = Exercise
        fields = ['id', 'stable_id', 'title', 'difficulty', 'description', 'is_solved']

    def get_is_solved(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Submission.objects.filter(author=request.user, exercise=obj, verdict=Submission.Verdict.ACCEPTED).exists()

class ChallengeSerializer(serializers.ModelSerializer):
    exercises = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    is_joined = serializers.SerializerMethodField()
    user_score = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()
    leaderboard = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            'id', 
            'stable_id', 
            'title', 
            'description', 
            'start_date', 
            'end_date', 
            'status',
            'is_joined', 
            'user_score', 
            'participants_count', 
            'exercises',
            'leaderboard'
        ]

    def get_status(self, obj):
        now = timezone.now()
        if now < obj.start_date:
            return 'UPCOMING'
        elif obj.start_date <= now <= obj.end_date:
            return 'ACTIVE'
        else:
            return 'FINISHED'

    def get_is_joined(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return ChallengeParticipation.objects.filter(challenge=obj, user=request.user).exists()

    def get_user_score(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        part = ChallengeParticipation.objects.filter(challenge=obj, user=request.user).first()
        return part.score if part else 0

    def get_participants_count(self, obj):
        return obj.participations.count()

    def get_exercises(self, obj):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        
        solved_ids = set()
        if user:
            solved_ids = set(Submission.objects.filter(
                author=user,
                exercise__in=obj.exercises.all(),
                verdict=Submission.Verdict.ACCEPTED
            ).values_list('exercise_id', flat=True))

        return [
            {
                'id': ex.id,
                'stable_id': ex.stable_id,
                'title': ex.title,
                'difficulty': ex.difficulty,
                'description': ex.statement,
                'is_solved': ex.id in solved_ids,
            }
            for ex in obj.exercises.all()
        ]

    def get_leaderboard(self, obj):
        parts = obj.participations.select_related('user').order_by('-score', 'joined_at')[:10]
        return [
            {
                'rank': idx + 1,
                'username': p.user.username,
                'full_name': p.user.full_name or p.user.username,
                'score': p.score,
                'joined_at': p.joined_at
            }
            for idx, p in enumerate(parts)
        ]

class ChallengeParticipationSerializer(serializers.ModelSerializer):
    challenge = ChallengeSerializer(read_only=True)
    challenge_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = ChallengeParticipation
        fields = ['id', 'challenge', 'challenge_id', 'score', 'joined_at']
