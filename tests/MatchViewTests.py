import logging
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from sidelines_django_app.models import Profile, Match, MatchVote, Team

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MatchViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpassword')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpassword')

        self.profile1 = Profile.objects.create(user=self.user1)
        self.profile2 = Profile.objects.create(user=self.user2)

        self.team1 = Team.objects.create(team_name='Team 1')
        self.team1.admins.add(self.profile1)
        self.team2 = Team.objects.create(team_name='Team 2')
        self.team2.admins.add(self.profile2)

        self.match = Match.objects.create(
            home_team=self.team1,
            away_team=self.team2,
            date_time='2024-12-01T15:00:00Z',
            location='Test Stadium',
        )

        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)

        logger.info('Setup complete')

    def authenticate(self, token):
        logger.info('Authenticating user with token: %s', token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_get_single_match(self):
        logger.info('Testing get_single_match')
        self.authenticate(self.token1.key)

        url = reverse('api:match-detail', kwargs={'match_id': self.match.pk})
        response = self.client.get(url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.match.pk)
        self.assertEqual(response.data['location'], self.match.location)
        self.assertEqual(response.data['home_team'], self.team1.pk)
        logger.info('test_get_single_match passed')

    def test_get_all_matches(self):
        logger.info('Testing get_all_matches')
        self.authenticate(self.token1.key)

        url = reverse('api:match-list')
        response = self.client.get(url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Match.objects.count())
        logger.info('test_get_all_matches passed')

    def test_vote_on_match(self):
        logger.info('Testing vote_on_match')
        self.authenticate(self.token1.key)

        url = reverse('api:vote', kwargs={'match_id': self.match.pk})
        data = {'vote': 'accepted'}
        response = self.client.post(url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(MatchVote.objects.filter(match=self.match, profile=self.profile1, response='accepted').exists())
        logger.info('test_vote_on_match passed')

    def test_vote_on_nonexistent_match(self):
        logger.info('Testing vote_on_nonexistent_match')
        self.authenticate(self.token1.key)

        url = reverse('api:vote', kwargs={'match_id': 9999})  # Non-existent match ID
        data = {'vote': 'accepted'}
        response = self.client.post(url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        logger.info('test_vote_on_nonexistent_match passed')

    def test_vote_with_invalid_response(self):
        logger.info('Testing vote_with_invalid_response')
        self.authenticate(self.token1.key)

        url = reverse('api:vote', kwargs={'match_id': self.match.pk})
        data = {'vote': 'invalid_response'}
        response = self.client.post(url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        logger.info('test_vote_with_invalid_response passed')

    def test_revote_on_match(self):
        logger.info('Testing revote_on_match')
        self.authenticate(self.token1.key)

        # Initial vote
        MatchVote.objects.create(match=self.match, profile=self.profile1, response='maybe')

        url = reverse('api:vote', kwargs={'match_id': self.match.pk})
        data = {'vote': 'accepted'}
        response = self.client.post(url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        match_vote = MatchVote.objects.get(match=self.match, profile=self.profile1)
        self.assertEqual(match_vote.response, 'accepted')
        logger.info('test_revote_on_match passed')
