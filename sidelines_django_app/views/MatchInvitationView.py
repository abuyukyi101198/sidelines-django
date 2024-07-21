from rest_framework import status
from rest_framework.response import Response

from sidelines_django_app.models import MatchInvitation, Team
from sidelines_django_app.serializers import MatchInvitationSerializer
from sidelines_django_app.views.BaseInvitationView import BaseInvitationView


class MatchInvitationView(BaseInvitationView):
    model = MatchInvitation
    serializer_class = MatchInvitationSerializer

    def get(self, request, request_type=None, request_id=None):
        # TODO: Implement
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_single_request(self, request_id):
        # TODO: Implement
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_all_requests(self, profile, request_type):
        # TODO: Implement (Replace profile with team? How?)
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def post(self, request):
        profile = request.user.profile

        from_team_id = request.data.get('from_team')
        to_team_id = request.data.get('to_team')
        team_size = request.data.get('team_size')
        location = request.data.get('location')
        date_time = request.data.get('date_time')

        try:
            from_team = Team.objects.get(pk=from_team_id)
            to_team = Team.objects.get(pk=to_team_id)
        except Team.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        error = self.validate_request('post', from_team=from_team, to_team=to_team, profile=profile)
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        invitation = self.model(from_team=from_team, to_team=to_team, team_size=team_size,
                                location=location, date_time=date_time)
        invitation.save()
        serializer = self.serializer_class(invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, match_invitation_id, action):
        profile = request.user.profile
        try:
            invitation = self.model.objects.get(pk=match_invitation_id)
        except self.model.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        error = self.validate_request('put', from_team=invitation.from_team,
                                      to_team=invitation.to_team, profile=profile)
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'accept':
            invitation.admin_approved = True
            invitation.save()
        elif action == 'ignore':
            invitation.delete()
        else:
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    def validate_request(self, request, from_team, to_team, profile):
        if request == 'post':
            if from_team == to_team:
                return 'Cannot send a match invitation to the same team.'
            elif profile not in from_team.members.all():
                return 'Cannot send a match invitation from a team you are not a member of.'
            elif profile not in from_team.admins.all():
                return 'Only admins can send match invitations.'
        elif request == 'put':
            if profile not in to_team.admins.all():
                return 'Cannot accept/ignore match invitations unless you are an admin.'
        return None

    def delete(self, request, request_id):
        # TODO: Implement
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
