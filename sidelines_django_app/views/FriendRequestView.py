from sidelines_django_app.models import FriendRequest
from sidelines_django_app.serializers import FriendRequestSerializer
from sidelines_django_app.views.BaseInvitationView import BaseInvitationView


class FriendRequestView(BaseInvitationView):
    model = FriendRequest
    serializer_class = FriendRequestSerializer
