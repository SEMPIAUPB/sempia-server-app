from rest_framework import generics, permissions
from .models import Submission
from .serializers import SubmissionSerializer, SubmissionCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class SubmissionListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubmissionCreateSerializer
        return SubmissionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN_TEACHER:
            return Submission.objects.all().order_by('-created_at')
        # Student sees only their own
        return Submission.objects.filter(author=user).order_by('-created_at')

class SubmissionDetailView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN_TEACHER:
            return Submission.objects.all()
        return Submission.objects.filter(author=user)
