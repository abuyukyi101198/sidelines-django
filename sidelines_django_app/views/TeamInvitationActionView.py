from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.models import TeamInvitation


class TeamInvitationActionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request, team_invitation_id, action):
        try:
            team_invitation = TeamInvitation.objects.get(pk=team_invitation_id)
            return TeamInvitationActionView.handle_action(request.user, team_invitation, action)
        except TeamInvitation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def handle_action(user, team_invitation, action):
        if action == 'accept':
            return TeamInvitationActionView.accept_request(user, team_invitation)
        elif action == 'ignore':
            return TeamInvitationActionView.ignore_request(user, team_invitation)
        elif action == 'withdraw':
            return TeamInvitationActionView.withdraw_request(user, team_invitation)
        else:
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def accept_request(user, team_invitation):
        if team_invitation.to_profile.user != user:
            return Response({'detail': 'You can only accept team invitations sent to you.'},
                            status=status.HTTP_403_FORBIDDEN)
        team_invitation.accept()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def ignore_request(user, team_invitation):
        if team_invitation.to_profile.user != user:
            return Response({'detail': 'You can only ignore team invitations sent to you.'},
                            status=status.HTTP_403_FORBIDDEN)
        team_invitation.ignore()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def withdraw_request(user, team_invitation):
        if team_invitation.from_profile.user != user:
            return Response({'detail': 'You can only withdraw team invitations sent by you.'},
                            status=status.HTTP_403_FORBIDDEN)
        team_invitation.delete()
        return Response(status=status.HTTP_200_OK)
