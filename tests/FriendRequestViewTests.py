import logging

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from sidelines_django_app.models import Profile, FriendRequest

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class FriendRequestViewTests(APITestCase):
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

        self.create_friend_request_url = reverse('api:create-friend-request')
        self.unfriend_url = reverse('api:unfriend', kwargs={'profile_id': self.profile2.pk})

        logger.info('Setup complete')

    def authenticate(self, token):
        logger.info('Authenticating user with token: %s', token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_get_single_friend_request(self):
        logger.info('Testing get_single_friend_request')
        self.authenticate(self.token1.key)

        friend_request = FriendRequest.objects.create(from_profile=self.profile1, to_profile=self.profile2)
        url = reverse('api:friend-request-detail', kwargs={'request_id': friend_request.pk})

        response = self.client.get(url)
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['from_profile'], self.profile1.pk)
        self.assertEqual(response.data['to_profile'], self.profile2.pk)
        logger.info('test_get_single_friend_request passed')

    def test_get_sent_friend_requests(self):
        logger.info('Testing get_sent_friend_requests')
        self.authenticate(self.token1.key)

        FriendRequest.objects.create(from_profile=self.profile1, to_profile=self.profile2)
        FriendRequest.objects.create(from_profile=self.profile2, to_profile=self.profile3)
        FriendRequest.objects.create(from_profile=self.profile1, to_profile=self.profile3)
        url = reverse('api:friend-request-list', kwargs={'request_type': 'sent'})

        response = self.client.get(url)
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.profile1.sent_requests.count())
        logger.info('test_get_sent_friend_requests passed')

    def test_get_received_friend_requests(self):
        logger.info('Testing get_received_friend_requests')
        self.authenticate(self.token1.key)

        FriendRequest.objects.create(from_profile=self.profile1, to_profile=self.profile2)
        FriendRequest.objects.create(from_profile=self.profile2, to_profile=self.profile3)
        FriendRequest.objects.create(from_profile=self.profile1, to_profile=self.profile3)
        url = reverse('api:friend-request-list', kwargs={'request_type': 'received'})

        response = self.client.get(url)
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.profile1.received_requests.count())
        logger.info('test_get_received_friend_requests passed')

    def test_send_friend_request(self):
        logger.info('Testing send_friend_request')
        self.authenticate(self.token1.key)

        data = {'to_profile': self.profile2.pk}
        response = self.client.post(self.create_friend_request_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FriendRequest.objects.filter(from_profile=self.profile1, to_profile=self.profile2).exists())
        logger.info('test_send_friend_request passed')

    def test_send_duplicate_friend_request(self):
        logger.info('Testing send_duplicate_friend_request')
        self.authenticate(self.token1.key)

        data = {'to_profile': self.profile2.pk}
        self.client.post(self.create_friend_request_url, data)

        response = self.client.post(self.create_friend_request_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Friend request already sent.', response.data['detail'])
        logger.info('test_send_duplicate_friend_request passed')

    def test_send_friend_request_to_self(self):
        logger.info('Testing send_friend_request_to_self')
        self.authenticate(self.token1.key)

        data = {'to_profile': self.profile1.pk}
        response = self.client.post(self.create_friend_request_url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot send a friend request to yourself.', response.data['detail'])
        logger.info('test_send_friend_request_to_self passed')

    def test_accept_friend_request(self):
        logger.info('Testing accept_friend_request')
        self.authenticate(self.token2.key)

        friend_request = FriendRequest.objects.create(from_profile=self.profile1, to_profile=self.profile2)
        url = reverse('api:friend-request-action', kwargs={'request_id': friend_request.pk, 'action': 'accept'})

        response = self.client.put(url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.profile2, self.profile1.friends.all())
        self.assertIn(self.profile1, self.profile2.friends.all())
        self.assertFalse(FriendRequest.objects.filter(from_profile=self.profile1, to_profile=self.profile2).exists())
        logger.info('test_accept_friend_request passed')

    def test_ignore_friend_request(self):
        logger.info('Testing ignore_friend_request')
        self.authenticate(self.token2.key)

        friend_request = FriendRequest.objects.create(from_profile=self.profile1, to_profile=self.profile2)
        url = reverse('api:friend-request-action', kwargs={'request_id': friend_request.pk, 'action': 'ignore'})

        response = self.client.put(url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.profile2, self.profile1.friends.all())
        self.assertNotIn(self.profile1, self.profile2.friends.all())
        self.assertFalse(FriendRequest.objects.filter(from_profile=self.profile1, to_profile=self.profile2).exists())
        logger.info('test_ignore_friend_request passed')

    def test_withdraw_friend_request(self):
        logger.info('Testing withdraw_friend_request')
        self.authenticate(self.token1.key)

        friend_request = FriendRequest.objects.create(from_profile=self.profile1, to_profile=self.profile2)
        url = reverse('api:friend-request-detail', kwargs={'request_id': friend_request.pk})

        response = self.client.delete(url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(FriendRequest.objects.filter(from_profile=self.profile1, to_profile=self.profile2).exists())
        logger.info('test_withdraw_friend_request passed')

    def test_unfriend(self):
        logger.info('Testing unfriend')
        self.authenticate(self.token1.key)

        self.profile1.friends.add(self.profile2)
        self.profile2.friends.add(self.profile1)

        response = self.client.delete(self.unfriend_url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.profile2, self.profile1.friends.all())
        self.assertNotIn(self.profile1, self.profile2.friends.all())
        logger.info('test_unfriend passed')

    def test_unfriend_non_friend(self):
        logger.info('Testing unfriend_non_friend')
        self.authenticate(self.token1.key)

        response = self.client.delete(self.unfriend_url)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This user is not in your friends list.', response.data['detail'])
        logger.info('test_unfriend_non_friend passed')
