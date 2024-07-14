from rest_framework import serializers
from sidelines_django_app.models import TeamInvitation


class TeamInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamInvitation
        fields = ('id', 'from_profile', 'to_profile', 'team', 'created_at')
