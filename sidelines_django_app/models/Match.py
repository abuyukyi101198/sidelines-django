from django.db import models

from sidelines_django_app.models import Team


class Match(models.Model):
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    team_size = models.IntegerField(default=7)
