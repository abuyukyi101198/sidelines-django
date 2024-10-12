from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.models import Profile
from sidelines_django_app.serializers import FriendSerializer


class ProfileSearchView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        query = request.GET.get('query')
        if not query:
            return Response({'detail': 'Query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        profiles = Profile.objects.filter(user__username__icontains=query) | Profile.objects.filter(
            user__first_name__icontains=query) | Profile.objects.filter(user__last_name__icontains=query)

        serializer = FriendSerializer(profiles, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
