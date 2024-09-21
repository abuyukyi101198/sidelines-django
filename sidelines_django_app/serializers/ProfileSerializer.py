from rest_framework import serializers

from sidelines_django_app.models import Profile, Team


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    friends = serializers.PrimaryKeyRelatedField(many=True, queryset=Profile.objects.all(), required=False)
    teams = serializers.PrimaryKeyRelatedField(many=True, queryset=Team.objects.all(), required=False)
    admin_teams = serializers.PrimaryKeyRelatedField(many=True, queryset=Team.objects.all(), required=False)

    class Meta:
        model = Profile
        fields = (
            'first_name', 'last_name', 'username', 'overall_rating', 'positions', 'kit_number', 'friends',
            'teams', 'admin_teams', 'join_date', 'date_of_birth', 'goals', 'assists', 'mvp',
        )
        read_only_fields = ('first_name', 'last_name', 'username', 'overall_rating', 'join_date',)
