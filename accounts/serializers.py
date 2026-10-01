from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'role', 'birth_date', 'is_student', 'university', 'current_semester', 'faculty', 'date_joined')
        read_only_fields = ('id', 'role', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    birth_date = serializers.DateField(required=False, allow_null=True)
    is_student = serializers.BooleanField(default=True)
    university = serializers.CharField(required=False, allow_blank=True, default='Universidad Pontificia Bolivariana')
    current_semester = serializers.IntegerField(required=False, allow_null=True)
    faculty = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'password', 'birth_date', 'is_student', 'university', 'current_semester', 'faculty')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            birth_date=validated_data.get('birth_date'),
            is_student=validated_data.get('is_student', True),
            university=validated_data.get('university', 'Universidad Pontificia Bolivariana'),
            current_semester=validated_data.get('current_semester'),
            faculty=validated_data.get('faculty', '')
        )
        # Create uninitialized skill progress for all skills
        from skills.models import Skill, UserSkillProgress
        skills = Skill.objects.all()
        progresses = [
            UserSkillProgress(user=user, skill=skill, is_initialized=False, mastery_percentage=0.0)
            for skill in skills
        ]
        UserSkillProgress.objects.bulk_create(progresses)
        return user

from rest_framework.exceptions import AuthenticationFailed

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        username = attrs.get('username')

        # Si el usuario ingresó un correo en el campo de username
        if username and '@' in username:
            try:
                user = User.objects.get(email=username)
                attrs['username'] = user.username
            except User.DoesNotExist:
                pass
        
        try:
            return super().validate(attrs)
        except Exception:
            raise AuthenticationFailed("Credenciales inválidas. Verifique su usuario/correo y contraseña.")

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
