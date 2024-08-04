import logging

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from sidelines_django_app.models import Profile, Team, TeamInvitation

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TeamInvitationViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpassword')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpassword')
        self.user3 = User.objects.create_user(username='user3', email='user3@example.com', password='testpassword')

        self.profile1 = Profile.objects.create(user=self.user1)
        self.profile2 = Profile.objects.create(user=self.user2)
        self.profile3 = Profile.objects.create(user=self.user3)

        self.profile1.friends.add(self.profile2)
        self.profile2.friends.add(self.profile1)

        self.team = Team.objects.create(team_name='Test Team')
        self.team.admins.add(self.profile1)

        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)

        self.create_team_invitation_url = reverse('api:create-team-invitation')

        logger.info('Setup complete')

    def authenticate(self, token):
        logger.info('Authenticating user with token: %s', token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_get_single_team_invitation(self):
        logger.info('Testing get_single_team_invitation')
        self.authenticate(self.token1.key)

        team_invitation = TeamInvitation.objects.create(from_profile=self.profile1, to_profile=self.profile2,
                                                        team=self.team)
        url = reverse('api:team-invitation-detail', kwargs={'request_id': team_invitation.pk})

        response = self.client.get(url)
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['from_profile'], self.profile1.pk)
        self.assertEqual(response.data['to_profile'], self.profile2.pk)
        self.assertEqual(response.data['team'], self.team.pk)
        logger.info('test_get_single_team_invitation passed')

    def test_get_sent_team_invitations(self):
        logger.info('Testing get_sent_team_invitations')
        self.authenticate(self.token1.key)

        TeamInvitation.objects.create(from_profile=self.profile1, to_profile=self.profile2, team=self.team)
        url = reverse('api:team-invitation-list', kwargs={'request_type': 'sent'})

        response = self.client.get(url)
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.profile1.sent_invitations.count())
        logger.info('test_get_sent_team_invitations passed')

    def test_get_received_team_invitations(self):
        logger.info('Testing get_received_team_invitations')
        self.authenticate(self.token2.key)

        TeamInvitation.objects.create(from_profile=self.profile1, to_profile=self.profile2, team=self.team)
        url = reverse('api:team-invitation-list', kwargs={'request_type': 'received'})

        response = self.client.get(url)
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.profile1.sent_invitations.count())
        logger.info('test_get_received_team_invitations passed')

    def test_send_team_invitation(self):
        logger.info('Testing send_team_invitation')
        self.authenticate(self.token1.key)

        data = {'to_profile': self.profile2.pk, 'team': self.team.pk}
        response = self.client.post(self.create_team_invitation_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TeamInvitation.objects.filter(from_profile=self.profile1, to_profile=self.profile2,
                                                      team=self.team).exists())
        logger.info('test_send_team_invitation passed')

    def test_send_team_invitation_to_self(self):
        logger.info('Testing send_team_invitation_to_self')
        self.authenticate(self.token1.key)

        data = {'to_profile': self.profile1.pk, 'team': self.team.pk}
        response = self.client.post(self.create_team_invitation_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot send a team invitation to yourself.', response.data['detail'])
        logger.info('test_send_team_invitation_to_self passed')

    def test_send_duplicate_team_invitation(self):
        logger.info('Testing send_duplicate_team_invitation')
        self.authenticate(self.token1.key)

        data = {'to_profile': self.profile2.pk, 'team': self.team.pk}
        self.client.post(self.create_team_invitation_url, data)

        response = self.client.post(self.create_team_invitation_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Team invitation already sent.', response.data['detail'])
        logger.info('test_send_duplicate_team_invitation passed')

    def test_send_team_invitation_to_non_friend(self):
        logger.info('Testing send_team_invitation_to_non_friend')
        self.authenticate(self.token1.key)

        data = {'to_profile': self.profile3.pk, 'team': self.team.pk}
        response = self.client.post(self.create_team_invitation_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Can only send team invitations to friends.', response.data['detail'])
        logger.info('test_send_team_invitation_to_non_friend passed')

    def test_send_team_invitation_to_existing_member(self):
        logger.info('Testing send_team_invitation_to_existing_member')
        self.authenticate(self.token1.key)

        self.team.members.add(self.profile2)

        data = {'to_profile': self.profile2.pk, 'team': self.team.pk}
        response = self.client.post(self.create_team_invitation_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This user is already in the team.', response.data['detail'])
        logger.info('test_send_team_invitation_to_existing_member passed')

    def test_send_team_invitation_as_non_admin(self):
        logger.info('Testing send_team_invitation_as_non_admin')
        self.authenticate(self.token2.key)

        self.team.members.add(self.profile2)

        self.profile2.friends.add(self.profile3)
        self.profile3.friends.add(self.profile2)

        data = {'to_profile': self.profile3.pk, 'team': self.team.pk}
        response = self.client.post(self.create_team_invitation_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Only admins can send team invitations.', response.data['detail'])
        logger.info('test_send_team_invitation_as_non_admin passed')

    def test_accept_team_invitation(self):
        logger.info('Testing accept_team_invitation')
        self.authenticate(self.token2.key)

        team_invitation = TeamInvitation.objects.create(from_profile=self.profile1, to_profile=self.profile2,
                                                        team=self.team)
        url = reverse('api:team-invitation-action', kwargs={'request_id': team_invitation.pk, 'action': 'accept'})

        response = self.client.put(url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.profile2, self.team.members.all())
        self.assertFalse(TeamInvitation.objects.filter(from_profile=self.profile1, to_profile=self.profile2,
                                                       team=self.team).exists())
        logger.info('test_accept_team_invitation passed')

    def test_ignore_team_invitation(self):
        logger.info('Testing ignore_team_invitation')
        self.authenticate(self.token2.key)

        team_invitation = TeamInvitation.objects.create(from_profile=self.profile1, to_profile=self.profile2,
                                                        team=self.team)
        url = reverse('api:team-invitation-action', kwargs={'request_id': team_invitation.pk, 'action': 'ignore'})

        response = self.client.put(url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.profile2, self.team.members.all())
        self.assertFalse(TeamInvitation.objects.filter(from_profile=self.profile1, to_profile=self.profile2,
                                                       team=self.team).exists())
        logger.info('test_ignore_team_invitation passed')

    def test_withdraw_team_invitation(self):
        logger.info('Testing withdraw_team_invitation')
        self.authenticate(self.token1.key)

        friend_request = TeamInvitation.objects.create(from_profile=self.profile1, to_profile=self.profile2,
                                                       team=self.team)
        url = reverse('api:team-invitation-detail', kwargs={'request_id': friend_request.pk})

        response = self.client.delete(url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(TeamInvitation.objects.filter(from_profile=self.profile1, to_profile=self.profile2,
                                                       team=self.team).exists())
        logger.info('test_withdraw_team_invitation passed')
