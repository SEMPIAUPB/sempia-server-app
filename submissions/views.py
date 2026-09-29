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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SubmissionTransition

class SubmissionCallbackView(APIView):
    # Depending on setup, this might need an API Key permission or specific service auth
    permission_classes = () # Allow any for now, but should validate token in real app

    def post(self, request, pk, *args, **kwargs):
        try:
            submission = Submission.objects.get(pk=pk)
        except Submission.DoesNotExist:
            return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)
            
        data = request.data
        verdict = data.get('state')
        time_used = data.get('time_used', 0)
        memory_used = data.get('memory_used', 0)
        error_msg = data.get('error_message', '')
        
        # Transition state
        SubmissionTransition.objects.create(
            submission=submission,
            previous_state=submission.state,
            new_state=Submission.State.COMPLETED,
            cause='Judgement finished'
        )
        
        submission.state = Submission.State.COMPLETED
        # Need to map Node 2 verdict state string to Django Verdict enum
        # Defaulting to whatever string comes for now
        submission.verdict = verdict 
        submission.time_used_ms = int(float(time_used) * 1000)
        submission.memory_used_kb = int(float(memory_used) / 1024)
        submission.error_details = error_msg
        
        submission.save()
        
        return Response({"status": "updated"})
