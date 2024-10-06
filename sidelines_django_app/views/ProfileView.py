from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.serializers import UserSerializer
from sidelines_django_app.serializers.profile import ProfileSerializer, ProfileSetupSerializer
from sidelines_django_app.serializers.profile.ProfilePictureSerializer import ProfilePictureSerializer


class ProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, pk=None):
        profile = request.user.profile
        if pk is None:
            serializer = ProfileSerializer(profile, context={'request': request})
        else:
            serializer = ProfileSerializer(pk=pk, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def patch(request):
        user = request.user
        user_serializer = UserSerializer(user, data=request.data, partial=True)

        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_serializer.save()

        profile = request.user.profile
        profile_serializer = ProfileSetupSerializer(profile, data=request.data)

        if profile_serializer.is_valid():
            profile_serializer.save()
            profile.setup_complete = True
            profile.save()
            profile_picture_serializer = ProfilePictureSerializer(profile, context={'request': request})
            return Response(profile_picture_serializer.data, status=status.HTTP_200_OK)
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
