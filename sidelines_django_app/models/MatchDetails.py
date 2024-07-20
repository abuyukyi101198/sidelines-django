from django.db import models

from sidelines_django_app.models import Match, Team


class MatchDetails(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='details')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    shooting = models.PositiveIntegerField(default=0)
    attacks = models.PositiveIntegerField(default=0)
    possession = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    fouls = models.PositiveIntegerField(default=0)
    corners = models.PositiveIntegerField(default=0)
