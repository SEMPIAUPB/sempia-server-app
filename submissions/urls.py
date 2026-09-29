from django.urls import path
from .views import SubmissionListCreateView, SubmissionDetailView

urlpatterns = [
    path('', SubmissionListCreateView.as_view(), name='submission_list_create'),
    path('<int:pk>/', SubmissionDetailView.as_view(), name='submission_detail'),
]
