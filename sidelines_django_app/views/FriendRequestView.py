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
    def get(request, friend_request_type=None, friend_request_id=None):
        if friend_request_id is not None:
            return FriendRequestView.get_single_friend_request(friend_request_id)

        profile = request.user.profile
        return FriendRequestView.get_all_friend_requests(profile, friend_request_type)

    @staticmethod
    def get_single_friend_request(friend_request_id):
        try:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            serializer = FriendRequestSerializer(friend_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FriendRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_all_friend_requests(profile, friend_request_type):
        if friend_request_type == 'sent':
            friend_requests = FriendRequest.objects.filter(from_profile=profile)
        elif friend_request_type == 'received':
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

    @staticmethod
    def put(request, friend_request_id, action):
        try:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            return FriendRequestView.process_action(request.user.profile, friend_request, action)
        except FriendRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def process_action(profile, friend_request, action):
        if action == 'accept':
            return FriendRequestView.process_accept(profile, friend_request)
        elif action == 'ignore':
            return FriendRequestView.process_ignore(profile, friend_request)
        else:
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def process_accept(profile, friend_request):
        if friend_request.to_profile != profile:
            return Response({'detail': 'You can only accept friend requests sent to you.'},
                            status=status.HTTP_403_FORBIDDEN)
        friend_request.accept()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def process_ignore(profile, friend_request):
        if friend_request.to_profile != profile:
            return Response({'detail': 'You can only ignore friend requests sent to you.'},
                            status=status.HTTP_403_FORBIDDEN)
        friend_request.ignore()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, friend_request_id):
        profile = request.user.profile

        try:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
        except FriendRequest.DoesNotExist:
            return Response({'detail': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)

        if friend_request.from_profile != profile:
            return Response({'detail': 'You can only withdraw friend requests sent by you.'},
                            status=status.HTTP_403_FORBIDDEN)
        friend_request.delete()
        return Response(status=status.HTTP_200_OK)
