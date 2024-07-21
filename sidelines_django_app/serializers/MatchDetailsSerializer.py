from rest_framework import serializers

from sidelines_django_app.models import MatchDetails


class MatchDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchDetails
        fields = '__all__'
