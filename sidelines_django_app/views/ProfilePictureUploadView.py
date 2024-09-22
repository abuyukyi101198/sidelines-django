from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class ProfilePictureUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile_picture = request.FILES.get('profile_picture')
        user_profile = request.user.profile

        if user_profile.profile_picture:
            old_picture_path = user_profile.profile_picture.path
            if default_storage.exists(old_picture_path):
                default_storage.delete(old_picture_path)

        user_profile.profile_picture = profile_picture
        user_profile.save()

        profile_picture_url = request.build_absolute_uri(user_profile.profile_picture.url)

        return Response({'profile_picture_url': profile_picture_url}, status=status.HTTP_200_OK)
