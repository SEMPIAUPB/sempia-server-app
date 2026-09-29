from rest_framework import serializers
from .models import Exercise, TestCase, ExerciseSkill
from skills.models import Skill
from django.contrib.auth import get_user_model

User = get_user_model()

class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['id', 'inputs', 'expected_outputs', 'case_type']

class SkillBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category']

class ExerciseListSerializer(serializers.ModelSerializer):
    skills = SkillBasicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Exercise
        fields = ['id', 'stable_id', 'title', 'difficulty', 'status', 'skills']

class ExerciseDetailSerializer(serializers.ModelSerializer):
    skills = SkillBasicSerializer(many=True, read_only=True)
    test_cases = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'stable_id', 'title', 'statement', 'difficulty',
            'time_limit_ms', 'memory_limit_kb', 'status', 'skills', 'test_cases'
        ]

    def get_test_cases(self, obj):
        # Only return visible test cases for normal requests
        # If it's an admin, we might want to return all, but this serializer is for students
        request = self.context.get('request')
        if request and request.user.role == User.Role.ADMIN_TEACHER:
            cases = obj.test_cases.all()
        else:
            cases = obj.test_cases.filter(case_type=TestCase.Type.VISIBLE)
        return TestCaseSerializer(cases, many=True).data

class ExerciseAdminCreateUpdateSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True, required=False)
    skill_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Exercise
        fields = [
            'stable_id', 'title', 'statement', 'difficulty',
            'time_limit_ms', 'memory_limit_kb', 'status', 'test_cases', 'skill_ids'
        ]

    def create(self, validated_data):
        test_cases_data = validated_data.pop('test_cases', [])
        skills_data = validated_data.pop('skill_ids', [])
        
        request = self.context.get('request')
        if request:
            validated_data['author'] = request.user
            
        exercise = Exercise.objects.create(**validated_data)
        
        for case_data in test_cases_data:
            TestCase.objects.create(exercise=exercise, **case_data)
            
        for skill in set(skills_data):
            ExerciseSkill.objects.create(exercise=exercise, skill=skill)
            
        return exercise

    def update(self, instance, validated_data):
        test_cases_data = validated_data.pop('test_cases', None)
        skills_data = validated_data.pop('skill_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if test_cases_data is not None:
            instance.test_cases.all().delete()
            for case_data in test_cases_data:
                TestCase.objects.create(exercise=instance, **case_data)
                
        if skills_data is not None:
            instance.exerciseskill_set.all().delete()
            for skill in set(skills_data):
                ExerciseSkill.objects.create(exercise=instance, skill=skill)
                
        return instance
