from rest_framework import serializers

from sidelines_django_app.models import Profile, FriendRequest


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    profile_picture = serializers.SerializerMethodField()

    is_friends = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
        'first_name', 'last_name', 'username', 'profile_picture', 'overall_rating', 'positions', 'kit_number', 'goals',
        'assists', 'mvp', 'date_of_birth', 'join_date', 'is_friends',
        )

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

    def get_is_friends(self, obj):
        request = self.context.get('request')
        if obj in request.user.profile.friends.all():
            return 'connected'
        elif FriendRequest.objects.filter(from_profile=request.user.profile, to_profile=obj).exists():
            return 'pending'
        return 'not connected'

    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields