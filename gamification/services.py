from django.db import transaction, IntegrityError
from django.utils import timezone
from .models import UserGamificationProfile, ExperienceEvent, UserAchievement, Achievement

def get_or_create_profile(user):
    profile, _ = UserGamificationProfile.objects.get_or_create(user=user)
    return profile

@transaction.atomic
def award_points(user, event_type, points, description, reference_id):
    """
    Idempotent operation to award points.
    """
    if ExperienceEvent.objects.filter(reference_id=reference_id).exists():
        return False, "Points already awarded for this reference."

    ExperienceEvent.objects.create(
        user=user,
        event_type=event_type,
        points_awarded=points,
        description=description,
        reference_id=reference_id
    )

    profile = get_or_create_profile(user)
    profile.points += points
    
    # Calculate level (simple logic: level = points // 100 + 1)
    profile.level = (profile.points // 100) + 1
    profile.save()
    
    return True, "Points awarded."

@transaction.atomic
def award_achievement(user, achievement_stable_id, reason):
    """
    Idempotent operation to award an achievement.
    """
    try:
        achievement = Achievement.objects.get(stable_id=achievement_stable_id)
    except Achievement.DoesNotExist:
        return False, "Achievement does not exist."
        
    if UserAchievement.objects.filter(user=user, achievement=achievement).exists():
        return False, "Achievement already unlocked."
        
    UserAchievement.objects.create(
        user=user,
        achievement=achievement,
        reason=reason
    )
    return True, "Achievement unlocked."
