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
    
    # Update Streak
    today = timezone.now().date()
    if profile.last_action_date != today:
        if profile.last_action_date == today - timezone.timedelta(days=1):
            profile.current_streak += 1
        else:
            profile.current_streak = 1
            
        if profile.current_streak > profile.highest_streak:
            profile.highest_streak = profile.current_streak
            
        profile.last_action_date = today

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
    user = submission.author
    exercise = submission.exercise
    from submissions.models import Submission
    from exercises.models import Exercise
    
    # 1. Award points (Idempotent per exercise so no farming)
    if submission.verdict == 'ACCEPTED':
        awarded, msg = award_points(
            user, 
            ExperienceEvent.EventType.EXERCISE_SOLVED, 
            10 + (exercise.difficulty // 10), # scale points with difficulty
            f'Resolvió el ejercicio: {exercise.title}', 
            f'solve_{user.id}_{exercise.id}'
        )
        
        # 2. Check Achievements
        # Total unique AC exercises
        ac_exercises_ids = Submission.objects.filter(author=user, verdict='ACCEPTED').values_list('exercise_id', flat=True).distinct()
        ac_count = ac_exercises_ids.count()
        
        if ac_count >= 1:
            award_achievement(user, 'ACH_FIRST_BLOOD', 'Primer problema resuelto.')
            
        # Fast Mind & Perfectionist (Solved on first attempt)
        submissions_for_this = Submission.objects.filter(author=user, exercise=exercise)
        if submissions_for_this.count() == 1:
            award_achievement(user, 'ACH_FAST_MIND', f'Resolviste {exercise.title} al primer intento.')
            
            # Check how many first attempt ACs they have
            # This is complex in a single query, so let's do a heuristic:
            # We can just count how many exercises have exactly 1 submission which is ACCEPTED
            # For simplicity, if they get here, they might have hit perfectionist.
            # We'll just run a query:
            from django.db.models import Count
            first_attempt_acs = Submission.objects.filter(author=user, verdict='ACCEPTED').values('exercise').annotate(c=Count('id')).filter(c=1).count()
            if first_attempt_acs >= 5:
                award_achievement(user, 'ACH_PERFECTIONIST', 'Resolviste 5 problemas distintos al primer intento.')
                
        # Persistent (Cazador de errores: 5 fails before AC)
        if submissions_for_this.count() >= 6:
            award_achievement(user, 'ACH_PERSISTENT', f'Persististe en {exercise.title} a pesar de los errores.')
            
        # Skill-based achievements
        # Graph King
        graph_skills = ['Representación de Grafos', 'Búsqueda en Anchura (BFS)', 'Búsqueda en Profundidad (DFS)', 'Topological Sort']
        graph_solved = Exercise.objects.filter(id__in=ac_exercises_ids, skills__name__in=graph_skills).distinct().count()
        if graph_solved >= 5:
            award_achievement(user, 'ACH_GRAPH_KING', 'Resolviste 5 problemas de grafos.')
            
        # Data Expert
        data_skills = ['Arreglos y Strings', 'Hash Tables / Maps', 'Pilas y Colas (Stacks & Queues)', 'Colas de Prioridad (Heaps)']
        data_solved = Exercise.objects.filter(id__in=ac_exercises_ids, skills__name__in=data_skills).distinct().count()
        if data_solved >= 10:
            award_achievement(user, 'ACH_DATA_EXPERT', 'Resolviste 10 problemas de estructuras de datos.')

        # DP Master
        dp_skills = ['Programación Dinámica Básica']
        dp_solved = Exercise.objects.filter(id__in=ac_exercises_ids, skills__name__in=dp_skills).distinct().count()
        if dp_solved >= 5:
            award_achievement(user, 'ACH_DP_MASTER', 'Resolviste 5 problemas de Programación Dinámica.')
            
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
                # Add points to challenge
                part.score += 100
                part.save()
                award_achievement(user, 'ACH_GLADIATOR', 'Participaste exitosamente en tu primer Reto Semanal.')

