from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

from .models import Exercise
from .serializers import (
    ExerciseListSerializer,
    ExerciseDetailSerializer,
    ExerciseAdminCreateUpdateSerializer
)

User = get_user_model()

class IsAdminTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.ADMIN_TEACHER)

class ExerciseListView(generics.ListAPIView):
    serializer_class = ExerciseListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['difficulty', 'skills__id']
    search_fields = ['title', 'stable_id']

    def get_queryset(self):
        user = self.request.user
        qs = Exercise.objects.filter(is_deleted=False)
        if user.role != User.Role.ADMIN_TEACHER:
            qs = qs.filter(status=Exercise.Status.PUBLISHED)
        return qs.distinct()

class ExerciseDetailView(generics.RetrieveAPIView):
    serializer_class = ExerciseDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'stable_id'

    def get_queryset(self):
        user = self.request.user
        qs = Exercise.objects.filter(is_deleted=False)
        if user.role != User.Role.ADMIN_TEACHER:
            qs = qs.filter(status=Exercise.Status.PUBLISHED)
        return qs

class ExerciseAdminCreateView(generics.CreateAPIView):
    queryset = Exercise.objects.filter(is_deleted=False)
    serializer_class = ExerciseAdminCreateUpdateSerializer
    permission_classes = (IsAdminTeacher,)

class ExerciseAdminUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exercise.objects.filter(is_deleted=False)
    serializer_class = ExerciseAdminCreateUpdateSerializer
    permission_classes = (IsAdminTeacher,)
    lookup_field = 'stable_id'

    def perform_destroy(self, instance):
        # Soft delete instead of hard delete if it has submissions, 
        # but to be safe we just always soft delete to preserve history.
        instance.is_deleted = True
        instance.save()
