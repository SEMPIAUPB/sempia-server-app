from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import UserGamificationProfile, UserAchievement, Challenge, ChallengeParticipation
from .serializers import (
    ProfileSerializer, 
    UserAchievementSerializer, 
    ChallengeSerializer, 
    ChallengeParticipationSerializer
)
from .services import get_or_create_profile

class GamificationProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return get_or_create_profile(self.request.user)

class GamificationRankingView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    
    def get_queryset(self):
        # Public ranking, ordered by points desc
        return UserGamificationProfile.objects.all().order_by('-points', 'user__username')

class UserAchievementsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserAchievementSerializer

    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user).order_by('-awarded_at')

class ChallengeListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChallengeSerializer

    def get_queryset(self):
        now = timezone.now()
        # Active challenges
        return Challenge.objects.filter(start_date__lte=now, end_date__gte=now)

class JoinChallengeView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChallengeParticipationSerializer

    def create(self, request, *args, **kwargs):
        challenge_id = request.data.get('challenge_id')
        try:
            challenge = Challenge.objects.get(stable_id=challenge_id)
        except Challenge.DoesNotExist:
            return Response({"detail": "Challenge not found."}, status=status.HTTP_404_NOT_FOUND)
            
        now = timezone.now()
        if not (challenge.start_date <= now <= challenge.end_date):
            return Response({"detail": "Challenge is not active."}, status=status.HTTP_400_BAD_REQUEST)
            
        if ChallengeParticipation.objects.filter(user=request.user, challenge=challenge).exists():
            return Response({"detail": "Already joined."}, status=status.HTTP_400_BAD_REQUEST)
            
        part = ChallengeParticipation.objects.create(user=request.user, challenge=challenge)
        serializer = self.get_serializer(part)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
