from django.urls import path
from .views import (
    UserSkillProgressView,
    DiagnosticExamView,
    SubmitDiagnosticExamView,
    RecommendedExercisesView
)

urlpatterns = [
    path('progress/', UserSkillProgressView.as_view(), name='skill_progress'),
    path('diagnostic/', DiagnosticExamView.as_view(), name='diagnostic_exam'),
    path('diagnostic/submit/', SubmitDiagnosticExamView.as_view(), name='submit_diagnostic_exam'),
    path('recommended/', RecommendedExercisesView.as_view(), name='recommended_exercises'),
]
