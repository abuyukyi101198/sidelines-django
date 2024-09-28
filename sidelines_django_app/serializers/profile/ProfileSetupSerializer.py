from rest_framework import serializers

from sidelines_django_app.models import Profile


class ProfileSetupSerializer(serializers.ModelSerializer):
    setup_complete = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'profile_picture', 'date_of_birth', 'positions', 'kit_number', 'setup_complete',
        )
        read_only_fields = ('setup_complete',)

    def get_setup_complete(self):
        return True
