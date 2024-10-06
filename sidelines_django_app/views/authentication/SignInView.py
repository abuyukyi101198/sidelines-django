from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from sidelines_django_app.serializers.profile.ProfilePictureSerializer import ProfilePictureSerializer


class SignInView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        identifier = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=identifier, password=password)

        if user is None:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            profile = user.profile
            profile_picture_serializer = ProfilePictureSerializer(profile, context={'request': request})
            if profile.setup_complete:
                return Response({'profile': profile_picture_serializer.data, 'token': token.key},
                                status=status.HTTP_200_OK)
            else:
                return Response({'token': token.key}, status=status.HTTP_206_PARTIAL_CONTENT)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
