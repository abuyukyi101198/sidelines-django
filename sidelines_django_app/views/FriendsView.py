from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.serializers import FriendListSerializer


class FriendsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        profile = request.user.profile
        serializer = FriendListSerializer(profile.friends.all(), context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)