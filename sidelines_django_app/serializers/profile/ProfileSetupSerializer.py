from rest_framework import serializers

from sidelines_django_app.models import Profile


class ProfileSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'profile_picture', 'date_of_birth', 'positions', 'kit_number', 'setup_complete',
        )
