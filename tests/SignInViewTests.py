import logging
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from sidelines_django_app.models import Profile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SignInViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users and profiles
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpassword')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpassword')

        # Create profiles for the users
        self.profile1 = Profile.objects.create(user=self.user1, setup_complete=True)
        self.profile2 = Profile.objects.create(user=self.user2, setup_complete=False)

        # Create token for user1
        self.token1 = Token.objects.create(user=self.user1)
        logger.info('Setup complete')

    def test_sign_in_with_username_success(self):
        """
        Test sign-in with a valid username and password, expecting a 200 OK response and a token.
        """
        url = '/api/signin/'
        data = {'username': 'user1', 'password': 'testpassword'}
        logger.info('Testing sign-in with username: %s', data['username'])

        response = self.client.post(url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['token'], self.token1.key)
        logger.info('test_sign_in_with_username_success passed')

    def test_sign_in_with_email_success(self):
        """
        Test sign-in with a valid email and password, expecting a 200 OK response and a token.
        """
        url = '/api/signin/'
        data = {'username': 'user1@example.com', 'password': 'testpassword'}
        logger.info('Testing sign-in with email: %s', data['username'])

        response = self.client.post(url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['token'], self.token1.key)
        logger.info('test_sign_in_with_email_success passed')

    def test_sign_in_partial_profile(self):
        """
        Test sign-in with a user whose profile setup is incomplete, expecting a 206 Partial Content response.
        """
        url = '/api/signin/'
        data = {'username': 'user2', 'password': 'testpassword'}
        logger.info('Testing sign-in with partial profile for user: %s', data['username'])

        response = self.client.post(url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_206_PARTIAL_CONTENT)
        self.assertIn('token', response.data)
        token = Token.objects.get(user=self.user2)
        self.assertEqual(response.data['token'], token.key)
        logger.info('test_sign_in_partial_profile passed')

    def test_sign_in_invalid_credentials(self):
        """
        Test sign-in with invalid credentials, expecting a 400 Bad Request response.
        """
        url = '/api/signin/'
        data = {'username': 'user1', 'password': 'wrongpassword'}
        logger.info('Testing sign-in with invalid credentials for user: %s', data['username'])

        response = self.client.post(url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid credentials')
        logger.info('test_sign_in_invalid_credentials passed')

    def test_sign_in_nonexistent_user(self):
        """
        Test sign-in with a non-existent username, expecting a 400 Bad Request response.
        """
        url = '/api/signin/'
        data = {'username': 'nonexistentuser', 'password': 'testpassword'}
        logger.info('Testing sign-in with nonexistent user: %s', data['username'])

        response = self.client.post(url, data)
        logger.debug('Response: %s', response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid credentials')
        logger.info('test_sign_in_nonexistent_user passed')
