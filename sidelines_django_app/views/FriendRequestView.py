from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.models import FriendRequest, Profile
from sidelines_django_app.serializers import FriendRequestSerializer


class FriendRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, request_type=None):
        profile = request.user.profile

        if request_type == 'sent':
            friend_requests = FriendRequest.objects.filter(from_profile=profile)
        elif request_type == 'received':
            friend_requests = FriendRequest.objects.filter(to_profile=profile)
        else:
            return Response({'detail': 'Invalid request type.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FriendRequestSerializer(friend_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        from_profile = request.user.profile

        to_profile_id = request.data.get('to_profile')
        try:
            to_profile = Profile.objects.get(pk=to_profile_id)
        except Profile.DoesNotExist:
            return Response({'detail': 'Recipient profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        error = FriendRequestView.validate_friend_request(from_profile, to_profile)
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest(from_profile=from_profile, to_profile=to_profile)
        friend_request.save()
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def validate_friend_request(from_profile, to_profile):
        if from_profile == to_profile:
            return 'Cannot send a friend request to yourself.'
        if FriendRequest.objects.filter(from_profile=from_profile, to_profile=to_profile).exists():
            return 'Friend request already sent.'
        if FriendRequest.objects.filter(from_profile=to_profile, to_profile=from_profile).exists():
            return 'Friend request already received from this user.'
        if to_profile in from_profile.friends.all():
            return 'This user is already your friend.'
        return None
