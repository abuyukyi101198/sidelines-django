from django.db import models

from sidelines_django_app.models import Team, Match


class MatchInvitation(models.Model):
    from_team = models.ForeignKey(Team, related_name='sent_invitations', on_delete=models.CASCADE)
    to_team = models.ForeignKey(Team, related_name='received_invitations', on_delete=models.CASCADE)
    team_size = models.IntegerField(default=7)
    location = models.CharField(max_length=255)
    date_time = models.DateTimeField()

    def accept(self):
        Match.objects.create(
            home_team=self.from_team,
            away_team=self.to_team,
            team_size=self.team_size,
            location=self.location,
            date_time=self.date_time
        )
        self.delete()

    def ignore(self):
        self.delete()
