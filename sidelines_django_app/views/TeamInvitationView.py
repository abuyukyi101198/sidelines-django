from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.models import TeamInvitation, Profile, Team
from sidelines_django_app.serializers import TeamInvitationSerializer


class TeamInvitationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, request_type=None):
        profile = request.user.profile

        if request_type == 'sent':
            team_invitations = TeamInvitation.objects.filter(from_profile=profile)
        elif request_type == 'received':
            team_invitations = TeamInvitation.objects.filter(to_profile=profile)
        else:
            return Response({'detail': 'Invalid request type.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TeamInvitationSerializer(team_invitations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        from_profile = request.user.profile

        to_profile_id = request.data.get('to_profile')
        team_id = request.data.get('team')
        try:
            to_profile = Profile.objects.get(pk=to_profile_id)
            team = Team.objects.get(pk=team_id)
        except (Profile.DoesNotExist, Team.DoesNotExist):
            return Response({'detail': 'Recipient profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        error = TeamInvitationView.validate_team_invitation(from_profile, to_profile, team)
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        team_invitation = TeamInvitation(from_profile=from_profile, to_profile=to_profile, team=team)
        team_invitation.save()
        serializer = TeamInvitationSerializer(team_invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def validate_team_invitation(from_profile, to_profile, team):
        if from_profile == to_profile:
            return 'Cannot send a team invitation to yourself.'
        if TeamInvitation.objects.filter(from_profile=from_profile, to_profile=to_profile).exists():
            return 'Team invitation already sent.'
        if to_profile in team.members.all():
            return 'This user is already in the team.'
        return None
