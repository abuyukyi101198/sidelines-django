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
    def get(request, team_invitation_type=None, team_invitation_id=None):
        if team_invitation_id is not None:
            return TeamInvitationView.get_single_team_invitation(team_invitation_id)

        profile = request.user.profile
        return TeamInvitationView.get_all_team_invitations(profile, team_invitation_type)

    @staticmethod
    def get_single_team_invitation(team_invitation_id):
        try:
            friend_request = TeamInvitation.objects.get(pk=team_invitation_id)
            serializer = TeamInvitationSerializer(friend_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TeamInvitation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_all_team_invitations(profile, team_invitation_type):
        if team_invitation_type == 'sent':
            team_invitations = TeamInvitation.objects.filter(from_profile=profile)
        elif team_invitation_type == 'received':
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

    @staticmethod
    def put(request, team_invitation_id, action):
        try:
            team_invitation = TeamInvitation.objects.get(pk=team_invitation_id)
            return TeamInvitationView.process_action(request.user.profile, team_invitation, action)
        except TeamInvitation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def process_action(profile, team_invitation, action):
        if action == 'accept':
            return TeamInvitationView.process_accept(profile, team_invitation)
        elif action == 'ignore':
            return TeamInvitationView.process_ignore(profile, team_invitation)
        else:
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def process_accept(profile, team_invitation):
        if team_invitation.to_profile != profile:
            return Response({'detail': 'You can only accept friend requests sent to you.'},
                            status=status.HTTP_403_FORBIDDEN)
        team_invitation.accept()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def process_ignore(profile, team_invitation):
        if team_invitation.to_profile != profile:
            return Response({'detail': 'You can only ignore friend requests sent to you.'},
                            status=status.HTTP_403_FORBIDDEN)
        team_invitation.ignore()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, team_invitation_id):
        profile = request.user.profile

        try:
            team_invitation = TeamInvitation.objects.get(pk=team_invitation_id)
        except TeamInvitation.DoesNotExist:
            return Response({'detail': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)

        if team_invitation.from_profile != profile:
            return Response({'detail': 'You can only withdraw friend requests sent by you.'},
                            status=status.HTTP_403_FORBIDDEN)
        team_invitation.delete()
        return Response(status=status.HTTP_200_OK)
