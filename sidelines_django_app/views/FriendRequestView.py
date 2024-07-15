from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from sidelines_django_app.models import FriendRequest, Profile
from sidelines_django_app.serializers import FriendRequestSerializer
from sidelines_django_app.views.BaseInvitationView import BaseInvitationView


class FriendRequestView(BaseInvitationView):
    model = FriendRequest
    serializer_class = FriendRequestSerializer

    def post(self, request):
        from_profile = request.user.profile

        to_profile_id = request.data.get('to_profile')
        try:
            to_profile = Profile.objects.get(pk=to_profile_id)
        except Profile.DoesNotExist:
            return Response({'detail': 'Recipient profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        error = self.validate_request(from_profile, to_profile)
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        request_obj = self.model(from_profile=from_profile, to_profile=to_profile)
        request_obj.save()
        serializer = self.serializer_class(request_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def validate_request(self, from_profile, to_profile):
        if from_profile == to_profile:
            return 'Cannot send a friend request to yourself.'
        if self.model.objects.filter(from_profile=from_profile, to_profile=to_profile).exists():
            return 'Friend request already sent.'
        if self.model.objects.filter(from_profile=to_profile, to_profile=from_profile).exists():
            return 'Friend request already received from this user.'
        if to_profile in from_profile.friends.all():
            return 'This user is already your friend.'
        return None

    @staticmethod
    @api_view(['DELETE'])
    def unfriend(request, profile_id):
        profile = request.user.profile

        try:
            other_profile = Profile.objects.get(pk=profile_id)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        if other_profile not in profile.friends.all():
            return Response({'detail': 'This user is not in your friends list.'}, status=status.HTTP_400_BAD_REQUEST)

        profile.unfriend(other_profile)
        return Response({'detail': 'Unfriended successfully.'}, status=status.HTTP_200_OK)
