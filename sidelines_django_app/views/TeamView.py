from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.models import Team, Profile
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

    @staticmethod
    @api_view(['PUT'])
    def promote_or_demote_member(request, team_id, member_id, action):
        team, member, error_response = TeamView.check_permissions_and_get_objects(request, team_id, member_id)
        if error_response:
            return error_response

        if action == 'promote':
            team.promote_member(member)
            return Response(status=status.HTTP_200_OK)
        elif action == 'demote':
            if member not in team.admins.all():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            team.demote_member(member)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    @api_view(['DELETE'])
    def remove_member(request, team_id, member_id):
        team, member, error_response = TeamView.check_permissions_and_get_objects(request, team_id, member_id)
        if error_response:
            return error_response

        team.remove_member(member)

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def check_permissions_and_get_objects(request, team_id, member_id):
        profile = request.user.profile
        try:
            team = Team.objects.get(pk=team_id)
            member = Profile.objects.get(pk=member_id)
        except (Team.DoesNotExist, Profile.DoesNotExist):
            return None, None, Response(status=status.HTTP_404_NOT_FOUND)

        if profile == member:
            return None, None, Response(status=status.HTTP_403_FORBIDDEN)

        if profile not in team.admins.all():
            return None, None, Response(status=status.HTTP_403_FORBIDDEN)

        if member not in team.members.all():
            return None, None, Response(status=status.HTTP_400_BAD_REQUEST)

        return team, member, None

    @staticmethod
    @api_view(['DELETE'])
    def leave(request, team_id):
        profile = request.user.profile

        try:
            team = Team.objects.get(pk=team_id)
        except Team.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if profile not in team.members.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if profile in team.admins.all() and team.admins.count() == 1 and team.members.count() > 1:
            return Response({'detail': 'You cannot leave the team as the last admin.'},
                            status=status.HTTP_403_FORBIDDEN)

        team.remove_member(profile)

        return Response(status=status.HTTP_200_OK)
