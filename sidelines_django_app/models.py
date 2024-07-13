from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
class Profile(models.Model):
    class Positions(models.TextChoices):
        GOALKEEPER = "GOALKEEPER", "Goalkeeper"
        DEFENDER = "DEFENDER", "Defender"
        MIDFIELDER = "MIDFIELDER", "Midfielder"
        STRIKER = "STRIKER", "Striker"
        ANY = "ANY", "Any"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    overall_rating = models.FloatField(default=0.0)
    position = models.CharField(max_length=10, choices=Positions.choices, default=Positions.ANY)
    kit_number = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(99)])
    friends = models.ManyToManyField('self', blank=True)
    pending_requests = models.ManyToManyField('self', symmetrical=False, through='FriendRequest', related_name='received_requests')
    join_date = models.DateField(auto_now_add=True)


class FriendRequest(models.Model):
    from_profile = models.ForeignKey(Profile, related_name='sent_requests', on_delete=models.CASCADE)
    to_profile = models.ForeignKey(Profile, related_name='received_requests', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
