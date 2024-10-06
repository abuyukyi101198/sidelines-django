import time

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from sidelines_django_app.serializers.profile.ProfilePictureSerializer import ProfilePictureSerializer


class VerifyTokenView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        profile_picture_serializer = ProfilePictureSerializer(profile, context={'request': request})
        return Response({'profile': profile_picture_serializer.data}, status=status.HTTP_200_OK)
