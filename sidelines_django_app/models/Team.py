from django.db import models


class Team(models.Model):
    team_name = models.CharField(max_length=100)
    overall_rating = models.FloatField(default=0.0)
    members = models.ManyToManyField('Profile', related_name='teams')
    admins = models.ManyToManyField('Profile', related_name='admin_teams')
    created_at = models.DateField(auto_now_add=True)

    def promote_member(self, member_profile):
        self.admins.add(member_profile)

    def demote_member(self, member_profile):
        self.admins.remove(member_profile)

    def remove_member(self, member_profile):
        self.members.remove(member_profile)
        if member_profile in self.admins.all():
            self.admins.remove(member_profile)
        if not self.members.exists():
            self.delete()
