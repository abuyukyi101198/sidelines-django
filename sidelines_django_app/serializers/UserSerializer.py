from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.contrib.auth.password_validation import validate_password

from sidelines_django_app.models import Profile
from sidelines_django_app.serializers.ProfileSerializer import ProfileSerializer


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    profile = ProfileSerializer()

    def validate_password(self, value):
        validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Profile.objects.create(user=user, **profile_data)
        return user

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'profile',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]
