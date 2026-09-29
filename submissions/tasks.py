from celery import shared_task
from .models import Submission, SubmissionTransition
import time
import random

@shared_task(queue='judge_submissions')
def judge_submission_task(submission_id):
    try:
        submission = Submission.objects.get(id=submission_id)
    except Submission.DoesNotExist:
        return
        
    # Transition to RUNNING
    SubmissionTransition.objects.create(
        submission=submission,
        previous_state=submission.state,
        new_state=Submission.State.RUNNING,
        cause='Picked up by judge worker'
    )
    submission.state = Submission.State.RUNNING
    submission.save()

    # Simulate adapter waiting for Judge0 or Node 2
    # In reality, this would send an HTTP request to Judge0 and poll or wait for callback.
    time.sleep(1) # simulate work
    
    # Randomly assign a verdict for the mock
    verdict = random.choice([
        Submission.Verdict.ACCEPTED, 
        Submission.Verdict.WRONG_ANSWER, 
        Submission.Verdict.TIME_LIMIT_EXCEEDED
    ])
    
    SubmissionTransition.objects.create(
        submission=submission,
        previous_state=submission.state,
        new_state=Submission.State.COMPLETED,
        cause='Judgement finished'
    )
    
    submission.state = Submission.State.COMPLETED
    submission.verdict = verdict
    submission.time_used_ms = random.randint(10, 900)
    submission.memory_used_kb = random.randint(1000, 50000)
    
    if verdict == Submission.Verdict.WRONG_ANSWER:
        submission.error_details = "Output mismatched on Test Case 2."
        
    submission.save()
    
    # Here we would also enqueue an AI review if it failed and the user wants a hint
    # ai_review_task.delay(...)
