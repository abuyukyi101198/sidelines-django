from django.db import models

from sidelines_django_app.models import Profile, Match


class MatchVote(models.Model):
    RESPONSE_CHOICES = [
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('maybe', 'Maybe'),
    ]
    match = models.ForeignKey(Match, related_name='votes', on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES, default='maybe')

    class Meta:
        unique_together = ('match', 'profile')
