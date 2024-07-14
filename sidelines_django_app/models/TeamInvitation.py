from django.db import models

from sidelines_django_app.models import Profile, Team


class TeamInvitation(models.Model):
    from_profile = models.ForeignKey(Profile, related_name='sent_invitations', on_delete=models.CASCADE)
    to_profile = models.ForeignKey(Profile, related_name='received_invitations', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='invitations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def accept(self):
        self.team.members.add(self.to_profile)
        self.delete()

    def ignore(self):
        self.delete()
