from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from sidelines_django_app.models import MatchInvitation, Team, MatchVote
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

    @staticmethod
    @api_view(['POST'])
    def vote(request, invitation_id):
        profile = request.user.profile
        vote_response = request.data.get('vote')

        if vote_response not in dict(MatchVote.RESPONSE_CHOICES):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = MatchInvitation.objects.get(pk=invitation_id)
        except MatchInvitation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not invitation.admin_approved:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            match_vote = MatchVote.objects.get(invitation=invitation, profile=profile)
        except MatchVote.DoesNotExist:
            match_vote = MatchVote(invitation=invitation, profile=profile)

        match_vote.response = vote_response
        match_vote.save()

        return Response(status=status.HTTP_200_OK)
