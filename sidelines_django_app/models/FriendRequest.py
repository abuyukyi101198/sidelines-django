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
