from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.validated_data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DashboardMetricsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        
        # 1. Learning Metrics from Submissions
        from submissions.models import Submission
        submissions = Submission.objects.filter(author=user)
        total_subs = submissions.count()
        ac_subs = submissions.filter(verdict='ACCEPTED')
        ac_count = ac_subs.count()
        
        problems_solved = ac_subs.values('exercise').distinct().count()
        
        success_rate = 0
        if total_subs > 0:
            success_rate = int((ac_count / total_subs) * 100)
            
        # Training hours: mock logic or sum of something? 
        # For a realistic mock based on activity: each submission ~ 15 minutes of work
        training_hours = round((total_subs * 15.0) / 60.0, 1)

        # 2. Gamification Streak
        from gamification.models import UserGamificationProfile
        profile = UserGamificationProfile.objects.filter(user=user).first()
        streak = profile.current_streak if profile else 0
        points = profile.points if profile else 0
        level = profile.level if profile else 1
        
        # Next level calculation (Level * 100)
        next_level_points = level * 100
        xp_in_level = points % 100
        progress_percentage = (xp_in_level / 100.0) * 100 if next_level_points > 0 else 0

        # 3. Top Skills
        from skills.models import UserSkillProgress
        skills_qs = UserSkillProgress.objects.filter(user=user, mastery_percentage__gt=0).order_by('-mastery_percentage')[:5]
        top_skills = [
            {"name": sp.skill.name, "percentage": int(sp.mastery_percentage)} 
            for sp in skills_qs
        ]
        
        return Response({
            "learning_metrics": {
                "problems_solved": problems_solved,
                "success_rate": success_rate,
                "current_streak": streak,
                "training_hours": training_hours
            },
            "gamification": {
                "points": points,
                "level": level,
                "next_level_points": next_level_points,
                "progress_percentage": progress_percentage
            },
            "top_skills": top_skills
        })
