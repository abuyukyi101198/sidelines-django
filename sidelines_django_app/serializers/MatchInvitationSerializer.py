from rest_framework import serializers

from sidelines_django_app.models import MatchInvitation
from sidelines_django_app.serializers.MatchVoteSerializer import MatchVoteSerializer


class MatchInvitationSerializer(serializers.ModelSerializer):
    votes = MatchVoteSerializer(many=True)

    class Meta:
        model = MatchInvitation
        fields = '__all__'
