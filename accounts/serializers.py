from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'role', 'date_joined')
        read_only_fields = ('id', 'role', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name']
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
        self.fields[self.username_field] = serializers.CharField(required=False)
        self.fields['email'] = serializers.EmailField(required=False)

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        if email and not username:
            try:
                user = User.objects.get(email=email)
                username = user.username
            except User.DoesNotExist:
                # Protect against enumeration
                pass
        
        attrs['username'] = username

        try:
            return super().validate(attrs)
        except Exception:
            # Generic message for enumeration protection
            raise AuthenticationFailed("No active account found with the given credentials")

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
