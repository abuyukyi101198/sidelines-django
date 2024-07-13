from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer


# Create your views here.
class UserRecordView(APIView):
    permission_classes = []

    @staticmethod
    def get(request, user_id=None):
        if user_id is not None:
            return UserRecordView.get_single_user(user_id)

        return UserRecordView.get_all_users()

    @staticmethod
    def get_single_user(user_id):
        try:
            user = User.objects.get(pk=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_all_users():
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


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


class FriendRequestActionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request, friend_request_id, action):
        try:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            return FriendRequestActionView.handle_action(request.user, friend_request, action)
        except FriendRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def handle_action(user, friend_request, action):
        if action == 'accept':
            return FriendRequestActionView.accept_request(user, friend_request)
        elif action == 'ignore':
            return FriendRequestActionView.ignore_request(user, friend_request)
        elif action == 'withdraw':
            return FriendRequestActionView.withdraw_request(user, friend_request)
        else:
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def accept_request(user, friend_request):
        if friend_request.to_profile.user != user:
            return Response({'detail': 'You can only accept friend requests sent to you.'},
                            status=status.HTTP_403_FORBIDDEN)
        friend_request.accept()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def ignore_request(user, friend_request):
        if friend_request.to_profile.user != user:
            return Response({'detail': 'You can only ignore friend requests sent to you.'},
                            status=status.HTTP_403_FORBIDDEN)
        friend_request.ignore()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def withdraw_request(user, friend_request):
        if friend_request.from_profile.user != user:
            return Response({'detail': 'You can only withdraw friend requests sent by you.'},
                            status=status.HTTP_403_FORBIDDEN)
        friend_request.delete()
        return Response(status=status.HTTP_200_OK)
