from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.models import Team, Profile


class PromoteDemoteMemberView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request, team_id, action, member_id):
        profile = request.user.profile

        try:
            team = Team.objects.get(pk=team_id)
            member = Profile.objects.get(pk=member_id)
        except (Team.DoesNotExist, Profile.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

        if profile not in team.admins.all():
            return Response(status=status.HTTP_403_FORBIDDEN)

        if member not in team.members.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if action == 'promote':
            team.admins.add(member)
            return Response(status=status.HTTP_200_OK)
        elif action == 'demote':
            if member not in team.admins.all():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            team.admins.remove(member)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
