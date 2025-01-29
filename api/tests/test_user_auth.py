from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework import status

from . import BaseTest
from .utils import create_test_user, PASSWORD, create_test_user_or_subject_details

class UserAuthTests(BaseTest):
    def setUp(self):
        self.client = APIClient()
        self.test_user = create_test_user()

    def test_user_gets_tokens_on_login(self):
        credentials = {
            "email": self.test_user.email,
            "password": PASSWORD
        }

        response = self.client.post(reverse("user_login"), data=credentials)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())


    def test_tokens_get_cleared_on_logout(self):
        self.access_token = str(AccessToken.for_user(self.test_user))
        self.refresh_token = str(RefreshToken.for_user(self.test_user))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        response = self.client.post(reverse("user_logout"), data={"refresh_token": self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

        # Clear test client's session state
        self.client.logout()

        response = self.client.get(reverse("overview"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_gets_tokens_on_register(self):
        data  = create_test_user_or_subject_details()
        response = self.client.post(reverse("user_register"), data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
        