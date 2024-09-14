import django.utils.timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    overall_rating = models.FloatField(default=0.0)
    positions = models.JSONField(default=list)
    kit_number = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(99)])
    friends = models.ManyToManyField('self', symmetrical=True)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    mvp = models.IntegerField(default=0)
    join_date = models.DateField(auto_now_add=True)
    setup_complete = models.BooleanField(default=False)
    date_of_birth = models.DateField(default=None, null=True, blank=True)

    def unfriend(self, other_profile):
        if self.friends.filter(pk=other_profile.pk).exists():
            self.friends.remove(other_profile)
            other_profile.friends.remove(self)
