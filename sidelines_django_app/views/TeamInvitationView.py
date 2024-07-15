from sidelines_django_app.models import TeamInvitation
from sidelines_django_app.serializers import TeamInvitationSerializer
from sidelines_django_app.views.BaseInvitationView import BaseInvitationView


class TeamInvitationView(BaseInvitationView):
    model = TeamInvitation
    serializer_class = TeamInvitationSerializer
