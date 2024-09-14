from rest_framework import serializers

from sidelines_django_app.models import Profile, Team


class ProfileSerializer(serializers.ModelSerializer):
    friends = serializers.PrimaryKeyRelatedField(many=True, queryset=Profile.objects.all(), required=False)
    teams = serializers.PrimaryKeyRelatedField(many=True, queryset=Team.objects.all(), required=False)
    admin_teams = serializers.PrimaryKeyRelatedField(many=True, queryset=Team.objects.all(), required=False)

    class Meta:
        model = Profile
        fields = (
            'overall_rating', 'positions', 'kit_number', 'friends', 'teams', 'admin_teams', 'join_date',
            'date_of_birth',)
        read_only_fields = ('overall_rating', 'join_date',)
