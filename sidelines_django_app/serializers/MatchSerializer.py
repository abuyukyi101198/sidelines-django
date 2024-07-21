from rest_framework import serializers

from sidelines_django_app.models import Match


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ('id', 'date_time', 'location', 'home_team', 'away_team', 'details',)
