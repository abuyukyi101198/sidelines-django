import logging

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from sidelines_django_app.models import Profile, Team, MatchInvitation

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MatchInvitationViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpassword')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpassword')
        self.user3 = User.objects.create_user(username='user3', email='user3@example.com', password='testpassword')

        self.profile1 = Profile.objects.create(user=self.user1)
        self.profile2 = Profile.objects.create(user=self.user2)
        self.profile3 = Profile.objects.create(user=self.user3)

        self.team1 = Team.objects.create(team_name='Team 1')
        self.team1.admins.add(self.profile1)
        self.team1.members.add(self.profile1)

        self.team2 = Team.objects.create(team_name='Team 2')
        self.team2.admins.add(self.profile2)
        self.team2.members.add(self.profile2)

        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)

        self.create_match_invitation_url = reverse('api:create-match-invitation')

        logger.info('Setup complete')

    def authenticate(self, token):
        logger.info('Authenticating user with token: %s', token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_get_single_match_invitation(self):
        logger.info('Testing get_single_match_invitation')
        self.authenticate(self.token1.key)

        match_invitation = MatchInvitation.objects.create(from_team=self.team1, to_team=self.team2,
                                                          team_size=11, location='Test Location',
                                                          date_time='2024-08-10T15:00:00Z')
        url = reverse('api:match-invitation-detail', kwargs={'request_id': match_invitation.pk})

        response = self.client.get(url)
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['from_team'], self.team1.pk)
        self.assertEqual(response.data['to_team'], self.team2.pk)
        self.assertEqual(response.data['team_size'], 11)
        self.assertEqual(response.data['location'], 'Test Location')
        logger.info('test_get_single_match_invitation passed')

    def test_get_sent_match_invitations(self):
        logger.info('Testing get_sent_match_invitations')
        self.authenticate(self.token1.key)

        MatchInvitation.objects.create(from_team=self.team1, to_team=self.team2,
                                       team_size=11, location='Test Location', date_time='2024-08-10T15:00:00Z')
        data = {'team': self.team1.pk}
        url = reverse('api:match-invitation-list', kwargs={'request_type': 'sent'})

        response = self.client.get(url, data)
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.team1.sent_invitations.count())
        logger.info('test_get_sent_match_invitations passed')

    def test_get_received_match_invitations(self):
        logger.info('Testing get_received_match_invitations')
        self.authenticate(self.token2.key)

        MatchInvitation.objects.create(from_team=self.team1, to_team=self.team2,
                                       team_size=11, location='Test Location', date_time='2024-08-10T15:00:00Z')
        data = {'team': self.team2.pk}
        url = reverse('api:match-invitation-list', kwargs={'request_type': 'received'})

        response = self.client.get(url, data)
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.team2.received_invitations.count())
        logger.info('test_get_received_match_invitations passed')

    def test_send_match_invitation(self):
        logger.info('Testing send_match_invitation')
        self.authenticate(self.token1.key)

        data = {'from_team': self.team1.pk, 'to_team': self.team2.pk, 'team_size': 11,
                'location': 'Test Location', 'date_time': '2024-08-10T15:00:00Z'}
        response = self.client.post(self.create_match_invitation_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(MatchInvitation.objects.filter(from_team=self.team1, to_team=self.team2).exists())
        logger.info('test_send_match_invitation passed')

    def test_send_match_invitation_to_same_team(self):
        logger.info('Testing send_match_invitation_to_same_team')
        self.authenticate(self.token1.key)

        data = {'from_team': self.team1.pk, 'to_team': self.team1.pk, 'team_size': 11,
                'location': 'Test Location', 'date_time': '2024-08-10T15:00:00Z'}
        response = self.client.post(self.create_match_invitation_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot send a match invitation to the same team.', response.data['detail'])
        logger.info('test_send_match_invitation_to_same_team passed')

    def test_send_match_invitation_as_non_admin(self):
        logger.info('Testing send_match_invitation_as_non_admin')
        self.authenticate(self.token2.key)

        self.team1.members.add(self.profile2)

        data = {'from_team': self.team1.pk, 'to_team': self.team2.pk, 'team_size': 11,
                'location': 'Test Location', 'date_time': '2024-08-10T15:00:00Z'}
        response = self.client.post(self.create_match_invitation_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Only admins can send match invitations.', response.data['detail'])
        logger.info('test_send_match_invitation_as_non_admin passed')

    def test_accept_match_invitation(self):
        logger.info('Testing accept_match_invitation')
        self.authenticate(self.token2.key)

        match_invitation = MatchInvitation.objects.create(from_team=self.team1, to_team=self.team2,
                                                          team_size=11, location='Test Location',
                                                          date_time='2024-08-10T15:00:00Z')
        url = reverse('api:match-invitation-action', kwargs={'request_id': match_invitation.pk, 'action': 'accept'})

        response = self.client.put(url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming logic to convert invitation to a match record
        self.assertFalse(MatchInvitation.objects.filter(pk=match_invitation.pk).exists())
        logger.info('test_accept_match_invitation passed')

    def test_ignore_match_invitation(self):
        logger.info('Testing ignore_match_invitation')
        self.authenticate(self.token2.key)

        match_invitation = MatchInvitation.objects.create(from_team=self.team1, to_team=self.team2,
                                                          team_size=11, location='Test Location',
                                                          date_time='2024-08-10T15:00:00Z')
        url = reverse('api:match-invitation-action', kwargs={'request_id': match_invitation.pk, 'action': 'ignore'})

        response = self.client.put(url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(MatchInvitation.objects.filter(pk=match_invitation.pk).exists())
        logger.info('test_ignore_match_invitation passed')

    def test_withdraw_match_invitation(self):
        logger.info('Testing withdraw_match_invitation')
        self.authenticate(self.token1.key)

        match_invitation = MatchInvitation.objects.create(from_team=self.team1, to_team=self.team2,
                                                          team_size=11, location='Test Location',
                                                          date_time='2024-08-10T15:00:00Z')
        url = reverse('api:match-invitation-detail', kwargs={'request_id': match_invitation.pk})

        response = self.client.delete(url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(MatchInvitation.objects.filter(pk=match_invitation.pk).exists())
        logger.info('test_withdraw_match_invitation passed')
