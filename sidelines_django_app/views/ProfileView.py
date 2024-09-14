from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.serializers import ProfileSerializer, UserSerializer


class ProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        user_serializer = UserSerializer(user, data=request.data, partial=True)

        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_serializer.save()

        profile = request.user.profile
        profile_serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if profile_serializer.is_valid():
            profile_serializer.save()
            profile.setup_complete = True
            profile.save()
            return Response(profile_serializer.data, status=status.HTTP_200_OK)
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
