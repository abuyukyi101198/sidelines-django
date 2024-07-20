from django.db import models

from sidelines_django_app.models import Team


class MatchInvitation(models.Model):
    from_team = models.ForeignKey(Team, related_name='sent_invitations', on_delete=models.CASCADE)
    to_team = models.ForeignKey(Team, related_name='received_invitations', on_delete=models.CASCADE)
    admin_approved = models.BooleanField(default=False)
    team_size = models.IntegerField(default=7)
    location = models.CharField(max_length=255)
    date_time = models.DateTimeField()
