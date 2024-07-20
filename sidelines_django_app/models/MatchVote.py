from django.db import models

from sidelines_django_app.models import MatchInvitation, Profile


class MatchVote(models.Model):
    RESPONSE_CHOICES = [
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('maybe', 'Maybe'),
        ('unvoted', 'Unvoted'),
    ]
    invitation = models.ForeignKey(MatchInvitation, related_name='votes', on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES, default='unvoted')

    class Meta:
        unique_together = ('invitation', 'profile')
