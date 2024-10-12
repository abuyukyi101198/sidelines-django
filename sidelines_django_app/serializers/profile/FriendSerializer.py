from rest_framework import serializers

from sidelines_django_app.models import Profile, Team


class FriendSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    profile_picture = serializers.SerializerMethodField()

    is_teammate = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'id', 'username', 'first_name', 'last_name', 'profile_picture', 'positions', 'is_teammate'
        )

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

    def get_is_teammate(self, obj):
        user = self.context.get('request').user
        user_teams = Team.objects.filter(members=user.profile)
        friend_teams = Team.objects.filter(members=obj)

        common_teams = user_teams & friend_teams

        return common_teams.exists()

    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields