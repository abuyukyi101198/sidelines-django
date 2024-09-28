from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from sidelines_django_app.models import Profile


class SignUpViewTests(APITestCase):

    def setUp(self):
        self.signup_url = '/api/signup/'
        self.user_data = {
            'password': 'strongpassword123',
            'email': 'test@example.com'
        }

    def test_signup_success(self):
        """
        Test case for successful user signup and token generation.
        """
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

        # Verify that the user and token are created.
        user = User.objects.get(email=self.user_data['email'])
        token = Token.objects.get(user=user)
        self.assertEqual(response.data['token'], token.key)
        self.assertEqual(user.email, 'test@example.com')

    def test_signup_missing_fields(self):
        """
        Test case for signup with missing required fields.
        """
        incomplete_data = self.user_data.copy()
        incomplete_data['password'] = ''  # Missing password
        response = self.client.post(self.signup_url, incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_signup_invalid_email(self):
        """
        Test case for signup with an invalid email format.
        """
        invalid_email_data = self.user_data.copy()
        invalid_email_data['email'] = 'invalid-email'  # Invalid email format
        response = self.client.post(self.signup_url, invalid_email_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_signup_user_already_exists(self):
        """
        Test case for attempting to signup with an already existing user.
        """
        User.objects.create_user(username='existinguser', password='password123', email='existing@example.com')

        duplicate_data = {
            'username': 'existinguser',
            'password': 'newpassword123',
            'email': 'newemail@example.com'
        }
        response = self.client.post(self.signup_url, duplicate_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)


class UsernameUniqueCheckTests(APITestCase):

    def setUp(self):
        self.check_url = '/api/username-unique-check/'
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpassword')

        self.profile1 = Profile.objects.create(user=self.user1)

        self.token = Token.objects.create(user=self.user1)

    def authenticate(self, token):
        """
        Helper method for authenticating requests with a token.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_username_unique_check_available(self):
        """
        Test case to check if a new username is available.
        """
        self.authenticate(self.token.key)
        data = {'username': 'newusername'}
        response = self.client.post(self.check_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_username_unique_check_taken(self):
        """
        Test case to check if an existing username is already taken.
        """
        self.authenticate(self.token.key)
        data = {'username': self.user1.username}
        response = self.client.post(self.check_url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_username_unique_check_missing_username(self):
        """
        Test case for missing username in the request body.
        """
        self.authenticate(self.token.key)
        response = self.client.post(self.check_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
