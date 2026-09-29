from django.db import models
from django.conf import settings
from exercises.models import Exercise

class Submission(models.Model):
    class State(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    class Verdict(models.TextChoices):
        ACCEPTED = 'ACCEPTED', 'Accepted'
        WRONG_ANSWER = 'WRONG_ANSWER', 'Wrong Answer'
        TIME_LIMIT_EXCEEDED = 'TIME_LIMIT_EXCEEDED', 'Time Limit Exceeded'
        MEMORY_LIMIT_EXCEEDED = 'MEMORY_LIMIT_EXCEEDED', 'Memory Limit Exceeded'
        RUNTIME_ERROR = 'RUNTIME_ERROR', 'Runtime Error'
        COMPILATION_ERROR = 'COMPILATION_ERROR', 'Compilation Error'
        INTERNAL_ERROR = 'INTERNAL_ERROR', 'Internal Error'
        NONE = 'NONE', 'None'

    # The author is immutable after creation.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='submissions')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='submissions')
    
    source_code = models.TextField()
    language = models.CharField(max_length=50)
    
    state = models.CharField(max_length=20, choices=State.choices, default=State.PENDING)
    verdict = models.CharField(max_length=50, choices=Verdict.choices, default=Verdict.NONE)
    
    time_used_ms = models.IntegerField(null=True, blank=True)
    memory_used_kb = models.IntegerField(null=True, blank=True)
    error_details = models.TextField(blank=True) # User allowed error details

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            original = Submission.objects.get(pk=self.pk)
            if original.author_id != self.author_id:
                raise ValueError("Author of a submission cannot be changed.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Submission {self.id} - {self.author.username} - {self.verdict}"

class SubmissionTransition(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='transitions')
    previous_state = models.CharField(max_length=20)
    new_state = models.CharField(max_length=20)
    cause = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.submission.id}: {self.previous_state} -> {self.new_state}"
