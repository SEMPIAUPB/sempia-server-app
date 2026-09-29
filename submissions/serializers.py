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
        
        # Enqueue Celery task
        from .tasks import judge_submission_task
        judge_submission_task.delay(submission.id)
        
        return submission
