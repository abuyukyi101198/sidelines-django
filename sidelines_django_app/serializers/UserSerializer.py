from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from sidelines_django_app.models import Profile
from sidelines_django_app.serializers.profile import ProfileSerializer


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    profile = ProfileSerializer(required=False)

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        Profile.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        return super().update(instance, validated_data)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'profile',
        )
        extra_kwargs = {
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'password': {'write_only': True}
        }
