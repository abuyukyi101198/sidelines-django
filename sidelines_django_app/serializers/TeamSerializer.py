from rest_framework import serializers
from sidelines_django_app.models import Profile, Team


class TeamSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=Profile.objects.all(), required=False)
    admins = serializers.PrimaryKeyRelatedField(many=True, queryset=Profile.objects.all(), required=False)

    class Meta:
        model = Team
        fields = ['id', 'team_name', 'overall_rating', 'members', 'admins', 'created_at',]
        read_only_fields = ['overall_rating', 'created_at',]
