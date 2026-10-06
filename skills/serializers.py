from rest_framework import serializers
from .models import Skill, UserSkillProgress, DiagnosticQuestion, DiagnosticChoice

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'description', 'category']

class UserSkillProgressSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    
    class Meta:
        model = UserSkillProgress
        fields = ['id', 'skill', 'mastery_percentage', 'is_initialized']

class DiagnosticChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticChoice
        fields = ['id', 'text']
        # Do not expose is_correct to the frontend

class DiagnosticQuestionSerializer(serializers.ModelSerializer):
    choices = DiagnosticChoiceSerializer(many=True, read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = DiagnosticQuestion
        fields = ['id', 'text', 'skill_name', 'choices']
