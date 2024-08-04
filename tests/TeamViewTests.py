import logging

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from sidelines_django_app.models import Profile, Team

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TeamViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpassword')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpassword')
        self.user3 = User.objects.create_user(username='user3', email='user3@example.com', password='testpassword')

        self.profile1 = Profile.objects.create(user=self.user1)
        self.profile2 = Profile.objects.create(user=self.user2)
        self.profile3 = Profile.objects.create(user=self.user3)

        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)

        self.team = Team.objects.create(team_name='Test Team')
        self.team.members.add(self.profile1)
        self.team.admins.add(self.profile1)

        self.team_url = reverse('api:team-detail', kwargs={'team_id': self.team.pk})
        self.leave_team_url = reverse('api:leave-team', kwargs={'team_id': self.team.pk})
        self.remove_member_url = reverse('api:remove-member',
                                         kwargs={'team_id': self.team.pk, 'member_id': self.profile2.pk})
        self.promote_member_url = reverse('api:promote-demote-member',
                                          kwargs={'team_id': self.team.pk, 'member_id': self.profile2.pk,
                                                  'action': 'promote'})

        logger.info('Setup complete')

    def authenticate(self, token):
        logger.info('Authenticating user with token: %s', token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_get_single_team(self):
        logger.info('Testing get_single_team')
        self.authenticate(self.token1.key)

        response = self.client.get(self.team_url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['team_name'], 'Test Team')
        logger.info('test_get_single_team passed')

    def test_get_all_teams(self):
        logger.info('Testing get_all_teams')
        self.authenticate(self.token1.key)

        url = reverse('api:team-list')
        response = self.client.get(url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        logger.info('test_get_all_teams passed')

    def test_create_team(self):
        logger.info('Testing create_team')
        self.authenticate(self.token1.key)

        data = {'team_name': 'New Team'}
        url = reverse('api:team-list')
        response = self.client.post(url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Team.objects.filter(team_name='New Team').exists())
        new_team = Team.objects.get(team_name='New Team')
        self.assertIn(self.profile1, new_team.members.all())
        self.assertIn(self.profile1, new_team.admins.all())
        logger.info('test_create_team passed')

    def test_update_team(self):
        logger.info('Testing update_team')
        self.authenticate(self.token1.key)

        data = {'team_name': 'Updated Team'}
        response = self.client.put(self.team_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['team_name'], 'Updated Team')
        logger.info('test_update_team passed')

    def test_delete_team(self):
        logger.info('Testing delete_team')
        self.authenticate(self.token1.key)

        response = self.client.delete(self.team_url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Team.objects.filter(pk=self.team.pk).exists())
        logger.info('test_delete_team passed')

    def test_promote_member(self):
        logger.info('Testing promote_member')
        self.authenticate(self.token1.key)

        self.team.members.add(self.profile2)

        response = self.client.put(self.promote_member_url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.profile2, self.team.admins.all())
        logger.info('test_promote_member passed')

    def test_remove_member(self):
        logger.info('Testing remove_member')
        self.authenticate(self.token1.key)

        self.team.members.add(self.profile2)

        response = self.client.delete(self.remove_member_url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.profile2, self.team.members.all())
        logger.info('test_remove_member passed')

    def test_leave_team(self):
        logger.info('Testing leave_team')
        self.authenticate(self.token2.key)

        self.team.members.add(self.profile2)
        response = self.client.delete(self.leave_team_url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.profile2, self.team.members.all())
        logger.info('test_leave_team passed')

    def test_leave_team_as_last_member(self):
        logger.info('Testing leave_team_as_last_member')
        self.authenticate(self.token1.key)

        team = Team.objects.create(team_name='Test Team')
        team.members.add(self.profile1)
        team.admins.add(self.profile1)

        leave_url = reverse('api:leave-team', kwargs={'team_id': team.pk})

        response = self.client.delete(leave_url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Team.objects.filter(pk=team.pk).exists())
        logger.info('test_leave_team_as_last_member passed')

    def test_leave_team_as_last_admin_with_members(self):
        logger.info('Testing leave_team_as_last_admin_with_members')
        self.authenticate(self.token1.key)

        team = Team.objects.create(team_name='Test Team')
        team.members.add(self.profile1, self.profile2)
        team.admins.add(self.profile1)

        leave_url = reverse('api:leave-team', kwargs={'team_id': team.pk})

        response = self.client.delete(leave_url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('You cannot leave the team as the last admin.', response.data['detail'])
        logger.info('test_leave_team_as_last_admin_with_members passed')

    def test_leave_team_as_admin_with_other_admins(self):
        logger.info('Testing leave_team_as_admin_with_other_admins')
        self.authenticate(self.token1.key)

        team = Team.objects.create(team_name='Test Team')
        team.members.add(self.profile1, self.profile2)
        team.admins.add(self.profile1, self.profile2)

        leave_url = reverse('api:leave-team', kwargs={'team_id': team.pk})

        response = self.client.delete(leave_url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.profile1, team.members.all())
        self.assertNotIn(self.profile1, team.admins.all())
        self.assertTrue(Team.objects.filter(pk=team.pk).exists())
        logger.info('test_leave_team_as_admin_with_other_admins passed')
