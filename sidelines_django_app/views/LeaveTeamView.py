from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.models import Team


class LeaveTeamView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request, team_id):
        profile = request.user.profile

        try:
            team = Team.objects.get(pk=team_id)
        except Team.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if profile not in team.members.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        team.members.remove(profile)

        if profile in team.admins.all():
            team.admins.remove(profile)

            if not team.admins.exists():
                remaining_members = team.members.all()
                if remaining_members.exists():
                    new_admin = remaining_members.order_by('?').first()
                    team.admins.add(new_admin)
                else:
                    team.delete()

        return Response(status=status.HTTP_200_OK)
