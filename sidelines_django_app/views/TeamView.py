from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.models import Team
from sidelines_django_app.serializers import TeamSerializer


class TeamView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, team_id=None):
        if team_id:
            return TeamView.get_single_team(team_id)

        return TeamView.get_all_teams()

    @staticmethod
    def get_single_team(team_id):
        try:
            team = Team.objects.get(pk=team_id)
            serializer = TeamSerializer(team)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_all_teams():
        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            team = serializer.save()
            profile = request.user.profile
            team.members.add(profile)
            team.admins.add(profile)
            team.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def put(request, team_id):
        try:
            team = Team.objects.get(pk=team_id)
            profile = request.user.profile
            if profile not in team.admins.all():
                return Response({'detail': 'You do not have permission to update this team.'},
                                status=status.HTTP_403_FORBIDDEN)
            serializer = TeamSerializer(team, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Team.DoesNotExist:
            return Response({'detail': 'Team not found.'}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def delete(request, team_id):
        try:
            team = Team.objects.get(pk=team_id)
            profile = request.user.profile
            if profile not in team.admins.all():
                return Response({'detail': 'You do not have permission to delete this team.'},
                                status=status.HTTP_403_FORBIDDEN)
            team.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Team.DoesNotExist:
            return Response({'detail': 'Team not found.'}, status=status.HTTP_404_NOT_FOUND)
