from django.urls import path
from .views import (
    ExerciseListView,
    ExerciseDetailView,
    ExerciseAdminCreateView,
    ExerciseAdminUpdateView
)

urlpatterns = [
    path('', ExerciseListView.as_view(), name='exercise_list'),
    path('<str:stable_id>/', ExerciseDetailView.as_view(), name='exercise_detail'),
    
    # Admin endpoints
    path('admin/create/', ExerciseAdminCreateView.as_view(), name='exercise_admin_create'),
    path('admin/<str:stable_id>/', ExerciseAdminUpdateView.as_view(), name='exercise_admin_update'),
]
