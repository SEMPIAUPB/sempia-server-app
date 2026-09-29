from django.urls import path
from .views import SubmissionListCreateView, SubmissionDetailView, SubmissionCallbackView

urlpatterns = [
    path('', SubmissionListCreateView.as_view(), name='submission_list_create'),
    path('<int:pk>/', SubmissionDetailView.as_view(), name='submission_detail'),
    path('<int:pk>/callback', SubmissionCallbackView.as_view(), name='submission_callback'),
]
