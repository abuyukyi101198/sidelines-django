from rest_framework import serializers

from sidelines_django_app.models import FriendRequest


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'from_profile', 'to_profile', 'created_at')
