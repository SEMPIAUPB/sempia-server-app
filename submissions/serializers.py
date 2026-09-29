from rest_framework import serializers
from .models import Submission, SubmissionTransition
from exercises.models import Exercise
from django.contrib.auth import get_user_model

User = get_user_model()

class SubmissionTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionTransition
        fields = ['id', 'previous_state', 'new_state', 'cause', 'created_at']

class SubmissionSerializer(serializers.ModelSerializer):
    transitions = SubmissionTransitionSerializer(many=True, read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    exercise_stable_id = serializers.CharField(source='exercise.stable_id', read_only=True)

    class Meta:
        model = Submission
        fields = [
            'id', 'author_username', 'exercise_stable_id', 'source_code', 'language',
            'state', 'verdict', 'time_used_ms', 'memory_used_kb', 'error_details',
            'created_at', 'updated_at', 'transitions'
        ]
        read_only_fields = [
            'state', 'verdict', 'time_used_ms', 'memory_used_kb', 'error_details',
            'created_at', 'updated_at', 'author_username', 'exercise_stable_id'
        ]

class SubmissionCreateSerializer(serializers.ModelSerializer):
    exercise_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = Submission
        fields = ['id', 'exercise_id', 'source_code', 'language', 'state', 'verdict']
        read_only_fields = ['state', 'verdict']

    def validate_exercise_id(self, value):
        try:
            # Normal user can only submit to PUBLISHED exercises
            exercise = Exercise.objects.get(stable_id=value, is_deleted=False)
            request = self.context.get('request')
            if request and request.user.role != User.Role.ADMIN_TEACHER:
                if exercise.status != Exercise.Status.PUBLISHED:
                    raise serializers.ValidationError("Exercise is not published.")
            return exercise
        except Exercise.DoesNotExist:
            raise serializers.ValidationError("Exercise does not exist.")

    def create(self, validated_data):
        exercise = validated_data.pop('exercise_id')
        request = self.context.get('request')
        
        submission = Submission.objects.create(
            author=request.user,
            exercise=exercise,
            state=Submission.State.PENDING,
            verdict=Submission.Verdict.NONE,
            **validated_data
        )
        
        # Map language to Judge0 language_id
        lang = submission.language.lower()
        language_id = 71 # default python
        if lang == 'cpp':
            language_id = 54
            
        # Enqueue real Celery task for Node 2
        contract_data = {
            "submission_id": str(submission.id),
            "exercise_id": str(exercise.stable_id),
            "source_code": submission.source_code,
            "language_id": language_id,
            "time_limit": exercise.time_limit_ms / 1000.0,
            "memory_limit": exercise.memory_limit_kb / 1024.0,
            "correlation_id": str(submission.id),
            "version": "1.0"
        }
        from config.celery import app as celery_app
        celery_app.send_task('worker.judge_submission', kwargs={"contract_data": contract_data}, queue='judge_submissions')
        
        return submission
