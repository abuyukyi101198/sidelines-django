from rest_framework import serializers

from sidelines_django_app.models import MatchVote


class MatchVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchVote
        fields = ('id', 'profile', 'response')
