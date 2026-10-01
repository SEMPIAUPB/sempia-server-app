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

def process_submission_gamification(submission):
    if submission.verdict == 'ACCEPTED':
        user = submission.author
        exercise = submission.exercise
        
        # 1. Award points
        award_points(
            user, 
            ExperienceEvent.EventType.EXERCISE_SOLVED, 
            10, 
            f'Resolvió el ejercicio: {exercise.title}', 
            f'solve_{submission.id}'
        )
        
        profile = get_or_create_profile(user)
        
        # 2. Check Achievements
        from submissions.models import Submission
        ac_count = Submission.objects.filter(author=user, verdict='ACCEPTED').count()
        if ac_count == 1:
            award_achievement(user, 'FIRST_AC', 'Primer ejercicio resuelto con éxito.')
            
        if ac_count >= 10:
            award_achievement(user, 'TEN_AC', '10 ejercicios resueltos con éxito.')
            
        # 3. Update Challenge Participation
        from gamification.models import Challenge, ChallengeParticipation
        now = timezone.now()
        active_challenges = Challenge.objects.filter(
            start_date__lte=now, 
            end_date__gte=now, 
            exercises=exercise
        )
        
        for challenge in active_challenges:
            part = ChallengeParticipation.objects.filter(user=user, challenge=challenge).first()
            if part:
                # Basic scoring: add 100 points to the challenge score for an AC
                # To prevent spamming, we should ideally check if it's the first AC for this exercise in this challenge.
                # For simplicity, we just add points.
                part.score += 100
                part.save()

