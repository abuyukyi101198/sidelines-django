from rest_framework import serializers

from sidelines_django_app.models import MatchInvitation


class MatchInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchInvitation
        fields = '__all__'
