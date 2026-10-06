from django.db import transaction
from .models import UserSkillProgress
from submissions.models import Submission

@transaction.atomic
def update_skill_progress(submission):
    """
    Called when a submission is evaluated. 
    RF-14: Update the graph mastery based on the result.
    Ensure that we only update it meaningfully.
    """
    if submission.verdict != 'ACCEPTED':
        # DKT normally decreases or adjusts mastery on failure.
        # For Sempia's current basic BKT implementation, let's keep it simple:
        # We might penalize slightly, or just do nothing.
        return
        
    user = submission.author
    exercise = submission.exercise
    
    # Check if this exercise was already solved by this user before
    previous_ac = Submission.objects.filter(
        author=user, 
        exercise=exercise, 
        verdict='ACCEPTED'
    ).exclude(id=submission.id).exists()
    
    if previous_ac:
        # The user has already solved this exercise, so we do not increase the graph mastery again.
        # RF-14 requirement: "que los ejercicios lo hagan una única vez al ser resuelto y se puedan saber cuáles ya ha resuelto"
        return
        
    # First time solving this exercise. Increase mastery for associated skills.
    skills = exercise.skills.all()
    for skill in skills:
        progress, _ = UserSkillProgress.objects.get_or_create(user=user, skill=skill)
        
        # Simple update formula: Add 15% mastery for a solved exercise, max 100%
        # A real DKT model would use Bayesian updates.
        new_mastery = progress.mastery_percentage + 15.0
        if new_mastery > 100.0:
            new_mastery = 100.0
            
        progress.mastery_percentage = new_mastery
        progress.is_initialized = True
        progress.save()
