from rest_framework import status
from rest_framework.response import Response

from sidelines_django_app.models import MatchInvitation, Team
from sidelines_django_app.serializers import MatchInvitationSerializer
from sidelines_django_app.views.BaseInvitationView import BaseInvitationView


class MatchInvitationView(BaseInvitationView):
    model = MatchInvitation
    serializer_class = MatchInvitationSerializer
    effect_class = Team
    from_field = 'from_team'
    to_field = 'to_team'

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

        error = self.validate_request(from_team=from_team, to_team=to_team, profile=profile)
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        invitation = self.model(from_team=from_team, to_team=to_team, team_size=team_size,
                                location=location, date_time=date_time)
        invitation.save()
        serializer = self.serializer_class(invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def validate_request(from_team, to_team, profile):
        if from_team == to_team:
            return 'Cannot send a match invitation to the same team.'
        elif profile not in from_team.members.all():
            return 'Cannot send a match invitation from a team you are not a member of.'
        elif profile not in from_team.admins.all():
            return 'Only admins can send match invitations.'
        return None
