from rest_framework import status
from rest_framework.response import Response

from sidelines_django_app.models import TeamInvitation, Profile, Team
from sidelines_django_app.serializers import TeamInvitationSerializer
from sidelines_django_app.views.BaseInvitationView import BaseInvitationView


class TeamInvitationView(BaseInvitationView):
    model = TeamInvitation
    serializer_class = TeamInvitationSerializer

    def post(self, request):
        from_profile = request.user.profile

        to_profile_id = request.data.get('to_profile')
        team_id = request.data.get('team')
        try:
            to_profile = Profile.objects.get(pk=to_profile_id)
            team = Team.objects.get(pk=team_id)
        except (Profile.DoesNotExist, Team.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

        error = self.validate_request(from_profile, to_profile, team)
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        request_obj = self.model(from_profile=from_profile, to_profile=to_profile, team=team)
        request_obj.save()
        serializer = self.serializer_class(request_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def validate_request(self, from_profile, to_profile, team):
        if from_profile not in team.admins.all():
            return 'Only admins can send team invitations.'
        if from_profile == to_profile:
            return 'Cannot send a team invitation to yourself.'
        if self.model.objects.filter(from_profile=from_profile, to_profile=to_profile).exists():
            return 'Team invitation already sent.'
        if self.model.objects.filter(from_profile=to_profile, to_profile=from_profile).exists():
            return 'Team invitation already received from this user.'
        if to_profile not in from_profile.friends.all():
            return 'Can only send team invitations to friends.'
        if to_profile in team.members.all():
            return 'This user is already in the team.'
        return None
