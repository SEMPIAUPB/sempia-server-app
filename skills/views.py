from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from .models import Skill, UserSkillProgress, DiagnosticQuestion, DiagnosticChoice
from .serializers import UserSkillProgressSerializer, DiagnosticQuestionSerializer
from exercises.models import Exercise

class UserSkillProgressView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSkillProgressSerializer
    pagination_class = None

    def get_queryset(self):
        # We also create missing profiles if needed
        skills = Skill.objects.all()
        for skill in skills:
            UserSkillProgress.objects.get_or_create(user=self.request.user, skill=skill)
            
        return UserSkillProgress.objects.filter(user=self.request.user)

class DiagnosticExamView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DiagnosticQuestionSerializer
    pagination_class = None

    def get_queryset(self):
        # Return a sample of questions (e.g. 1 per skill) to keep it brief
        # For a real app, we'd randomly select or use a specific exam set
        return DiagnosticQuestion.objects.all()

class SubmitDiagnosticExamView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        answers = request.data.get('answers', []) # format: [{"question_id": 1, "choice_id": 2}]
        user = request.user
        
        # Calculate scores per skill
        skill_scores = {}
        skill_counts = {}
        
        for answer in answers:
            try:
                question = DiagnosticQuestion.objects.get(id=answer['question_id'])
                choice = DiagnosticChoice.objects.get(id=answer['choice_id'], question=question)
                
                skill = question.skill
                if skill not in skill_scores:
                    skill_scores[skill] = 0
                    skill_counts[skill] = 0
                    
                skill_counts[skill] += 1
                if choice.is_correct:
                    skill_scores[skill] += 1
            except (DiagnosticQuestion.DoesNotExist, DiagnosticChoice.DoesNotExist):
                continue
                
        # Apply initial mastery (e.g., max 40% based on the exam)
        for skill, score in skill_scores.items():
            progress, _ = UserSkillProgress.objects.get_or_create(user=user, skill=skill)
            
            # if they get all questions for this skill correct -> 40% mastery
            percentage = (score / skill_counts[skill]) * 40.0
            
            # update only if not initialized or if this new score is higher
            if not progress.is_initialized or percentage > progress.mastery_percentage:
                progress.mastery_percentage = percentage
                progress.is_initialized = True
                progress.save()
                

                
        return Response({"status": "Exam processed successfully."})

class RecommendedExercisesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # Get skills where mastery < 90% (meaning they still need to learn it)
        # But prerequisites must have mastery > 60% (meaning they are ready)
        progresses = UserSkillProgress.objects.filter(user=user)
        progress_dict = {p.skill.id: p.mastery_percentage for p in progresses}
        
        ready_skills = []
        for p in progresses:
            if p.mastery_percentage < 90.0:
                # check prereqs
                prereqs = p.skill.prerequisites.all()
                is_ready = True
                for prereq in prereqs:
                    if progress_dict.get(prereq.id, 0.0) < 60.0:
                        is_ready = False
                        break
                
                if is_ready:
                    ready_skills.append(p.skill)
                    
        # If no strict ready skills, just pick the ones with lowest mastery overall
        if not ready_skills:
            ready_skills = [p.skill for p in progresses.order_by('mastery_percentage')[:3]]
            
        # Get exercises that teach these skills
        recommended_exercises = Exercise.objects.filter(skills__in=ready_skills).distinct()[:10]
        
        from exercises.serializers import ExerciseListSerializer
        serializer = ExerciseListSerializer(recommended_exercises, many=True)
        return Response(serializer.data)
