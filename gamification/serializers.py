from rest_framework import serializers
from .models import UserGamificationProfile, Achievement, UserAchievement, Challenge, ChallengeParticipation
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserGamificationProfile
        fields = ['username', 'points', 'level', 'current_streak', 'highest_streak']

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['stable_id', 'title', 'description', 'image_url']

class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = ['achievement', 'awarded_at', 'reason']

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['stable_id', 'title', 'description', 'start_date', 'end_date']

class ChallengeParticipationSerializer(serializers.ModelSerializer):
    challenge = ChallengeSerializer(read_only=True)
    challenge_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = ChallengeParticipation
        fields = ['challenge', 'challenge_id', 'score', 'joined_at']
