import logging

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from sidelines_django_app.models import Profile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class UserRecordViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.profile = Profile.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url_list = reverse('api:user-list')
        self.url_detail = reverse('api:user-detail', kwargs={'user_id': self.user.pk})
        logger.info('Setup complete')

    def test_get_all_users(self):
        logger.info('Testing get_all_users')
        response = self.client.get(self.url_list)
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), User.objects.count())
        self.assertEqual(User.objects.count(), Profile.objects.count())
        logger.info('test_get_all_users passed')

    def test_get_single_user(self):
        logger.info('Testing get_single_user')
        response = self.client.get(self.url_detail)
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        logger.info('test_get_single_user passed')

    def test_get_single_user_not_found(self):
        logger.info('Testing get_single_user_not_found')
        response = self.client.get(reverse('api:user-detail', kwargs={'user_id': 999}))
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        logger.info('test_get_single_user_not_found passed')

    def test_create_user(self):
        logger.info('Testing create_user')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'profile': {
                'position': 'MIDFIELDER',
                'kit_number': 7
            }
        }
        response = self.client.post(self.url_list, data, format='json')
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Profile.objects.filter(user__username='newuser').exists())
        logger.info('test_create_user passed')

    def test_create_user_invalid(self):
        logger.info('Testing create_user_invalid')
        data = {
            'username': '',
            'email': 'invalidemail',
            'password': 'pw',
            'first_name': '',
            'last_name': '',
            'profile': {
                'position': '',
                'kit_number': 100
            }
        }
        response = self.client.post(self.url_list, data, format='json')
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        logger.info('test_create_user_invalid passed')

    def test_delete_user(self):
        logger.info('Testing delete_user')
        response = self.client.delete(self.url_detail)
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
        self.assertFalse(Profile.objects.filter(user__pk=self.user.pk).exists())
        logger.info('test_delete_user passed')

    def test_delete_user_not_found(self):
        logger.info('Testing delete_user_not_found')
        response = self.client.delete(reverse('api:user-detail', kwargs={'user_id': 999}))
        logger.debug('Response: %s', response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        logger.info('test_delete_user_not_found passed')
