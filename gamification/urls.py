from django.urls import path
from .views import (
    GamificationProfileView,
    GamificationRankingView,
    UserAchievementsView,
    ChallengeListView,
    JoinChallengeView
)

urlpatterns = [
    path('profile/', GamificationProfileView.as_view(), name='gamification_profile'),
    path('ranking/', GamificationRankingView.as_view(), name='gamification_ranking'),
    path('achievements/', UserAchievementsView.as_view(), name='gamification_achievements'),
    path('challenges/', ChallengeListView.as_view(), name='gamification_challenges'),
    path('challenges/join/', JoinChallengeView.as_view(), name='gamification_join_challenge'),
]
