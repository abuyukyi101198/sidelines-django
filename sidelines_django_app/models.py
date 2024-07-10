from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.
class Profile(models.Model):
    class Positions(models.TextChoices):
        GOALKEEPER = "GOALKEEPER", "Goalkeeper"
        DEFENDER = "DEFENDER", "Defender"
        MIDFIELDER = "MIDFIELDER", "Midfielder"
        STRIKER = "STRIKER", "Striker"
        ANY = "ANY", "Any"

    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    overall_rating = models.FloatField(default=0.0)
    position = models.CharField(max_length=10, choices=Positions.choices, default=Positions.ANY)
    kit_number = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(99)])
    join_date = models.DateField(auto_now_add=True)


# @receiver(post_save, sender=User)
# def create_or_update_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#     else:
#         instance.profile.save()
