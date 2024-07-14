from rest_framework import serializers

from sidelines_django_app.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    friends = serializers.PrimaryKeyRelatedField(many=True, queryset=Profile.objects.all(), required=False)

    class Meta:
        model = Profile
        fields = ('overall_rating', 'position', 'kit_number', 'friends', 'teams', 'admin_teams', 'join_date',)
        read_only_fields = ('overall_rating', 'join_date',)
