from django.db import models

from sidelines_django_app.models import Profile


class FriendRequest(models.Model):
    from_profile = models.ForeignKey(Profile, related_name='sent_requests', on_delete=models.CASCADE)
    to_profile = models.ForeignKey(Profile, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def accept(self):
        self.from_profile.friends.add(self.to_profile)
        self.to_profile.friends.add(self.from_profile)
        self.delete()

    def ignore(self):
        self.delete()

    def save(self, *args, **kwargs):
        if self.from_profile == self.to_profile:
            raise ValueError("Cannot send a friend request to yourself.")

        if FriendRequest.objects.filter(from_profile=self.from_profile, to_profile=self.to_profile).exists():
            raise ValueError("Friend request already sent.")

        if FriendRequest.objects.filter(from_profile=self.to_profile, to_profile=self.from_profile).exists():
            raise ValueError("Friend request already received from this user.")

        if self.to_profile in self.from_profile.friends.all():
            raise ValueError("This user is already your friend.")

        super().save(*args, **kwargs)
