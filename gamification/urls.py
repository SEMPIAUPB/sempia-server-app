from django.urls import path
from .views import (
    GamificationProfileView,
    GamificationRankingView,
    CatalogAchievementsView,
    ChallengeListView,
    ChallengeDetailView,
    JoinChallengeView
)

urlpatterns = [
    path('profile/', GamificationProfileView.as_view(), name='gamification_profile'),
    path('ranking/', GamificationRankingView.as_view(), name='gamification_ranking'),
    path('achievements/', CatalogAchievementsView.as_view(), name='gamification_achievements'),
    path('challenges/join/', JoinChallengeView.as_view(), name='gamification_join_challenge'),
    path('challenges/', ChallengeListView.as_view(), name='gamification_challenges'),
    path('challenges/<str:stable_id>/', ChallengeDetailView.as_view(), name='gamification_challenge_detail'),
]
