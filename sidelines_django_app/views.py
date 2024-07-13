from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile, FriendRequest
from .serializers import UserSerializer, ProfileSerializer, FriendRequestSerializer


# Create your views here.
class UserRecordView(APIView):
    permission_classes = []

    @staticmethod
    def get(request, user_id=None):
        if user_id is not None:
            try:
                user = User.objects.get(pk=user_id)
                serializer = UserSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

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


class FriendListView(APIView):
    def get(self, request, profile_id):
        try:
            profile = Profile.objects.get(pk=profile_id)
            friends = profile.friends.all()
            serializer = ProfileSerializer(friends, many=True)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, profile_id):
        try:
            profile = Profile.objects.get(pk=profile_id)
            friend_id = request.data.get('friend_id')
            friend = Profile.objects.get(pk=friend_id)
            profile.friends.add(friend)
            return Response(status=status.HTTP_201_CREATED)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, profile_id, friend_id):
        try:
            profile = Profile.objects.get(pk=profile_id)
            friend = Profile.objects.get(pk=friend_id)
            profile.friends.remove(friend)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FriendRequestListView(APIView):
    def post(self, request, from_profile_id, to_profile_id):
        try:
            from_profile = Profile.objects.get(pk=from_profile_id)
            to_profile = Profile.objects.get(pk=to_profile_id)

            if from_profile == to_profile:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            existing_request = FriendRequest.objects.filter(from_profile=from_profile, to_profile=to_profile)
            if existing_request.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            friend_request = FriendRequest.objects.create(from_profile=from_profile, to_profile=to_profile)
            serializer = FriendRequestSerializer(friend_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, request_id):
        try:
            friend_request = FriendRequest.objects.get(pk=request_id)
            friend_request.is_accepted = True
            friend_request.save()
            return Response(status=status.HTTP_200_OK)
        except FriendRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, request_id):
        try:
            friend_request = FriendRequest.objects.get(pk=request_id)
            friend_request.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FriendRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
