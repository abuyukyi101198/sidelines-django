from django.db import models


class Team(models.Model):
    team_name = models.CharField(max_length=100)
    overall_rating = models.FloatField(default=0.0)
    members = models.ManyToManyField('Profile', related_name='teams')
    admins = models.ManyToManyField('Profile', related_name='admin_teams')
    created_at = models.DateField(auto_now_add=True)
