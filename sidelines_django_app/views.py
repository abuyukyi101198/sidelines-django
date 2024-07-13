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
            try:
                user = User.objects.get(pk=user_id)
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

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

    def get(self, request, request_type=None):
        profile = request.user.profile

        if request_type == 'sent':
            friend_requests = FriendRequest.objects.filter(from_profile=profile)
        elif request_type == 'received':
            friend_requests = FriendRequest.objects.filter(to_profile=profile)
        else:
            return Response({'detail': 'Invalid request type.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FriendRequestSerializer(friend_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        from_profile = request.user.profile

        to_profile_id = request.data.get('to_profile')
        try:
            to_profile = Profile.objects.get(pk=to_profile_id)
        except Profile.DoesNotExist:
            return Response({'detail': 'Recipient profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        if from_profile == to_profile:
            return Response({'detail': 'Cannot send a friend request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(from_profile=from_profile, to_profile=to_profile).exists():
            return Response({'detail': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(from_profile=to_profile, to_profile=from_profile).exists():
            return Response({'detail': 'Friend request already received from this user.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if to_profile in from_profile.friends.all():
            return Response({'detail': 'This user is already your friend.'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest(from_profile=from_profile, to_profile=to_profile)
        friend_request.save()
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FriendRequestActionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, friend_request_id, action):
        try:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            if action == 'accept':
                if friend_request.to_profile.user != request.user:
                    return Response({'detail': 'You can only accept friend requests sent to you.'},
                                    status=status.HTTP_403_FORBIDDEN)
                friend_request.accept()
            elif action == 'ignore':
                if friend_request.to_profile.user != request.user:
                    return Response({'detail': 'You can only ignore friend requests sent to you.'},
                                    status=status.HTTP_403_FORBIDDEN)
                friend_request.ignore()
            elif action == 'withdraw':
                if friend_request.from_profile.user != request.user:
                    return Response({'detail': 'You can only withdraw friend requests sent by you.'},
                                    status=status.HTTP_403_FORBIDDEN)
                friend_request.delete()
            else:
                return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)
        except FriendRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
