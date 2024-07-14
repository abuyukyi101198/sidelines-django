from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


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
    friends = models.ManyToManyField('self', symmetrical=True)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    mvp = models.IntegerField(default=0)
    join_date = models.DateField(auto_now_add=True)
