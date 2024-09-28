from rest_framework import serializers

from sidelines_django_app.models import Profile
from sidelines_django_app.serializers.profile.FriendSerializer import FriendSerializer


class FriendListSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ('friends', )
        read_only_fields = ('friends', )
