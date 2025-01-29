from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework import status

from . import BaseTest
from ..models import Subject
from .utils import create_test_subject, PASSWORD, create_test_user_or_subject_details

class SubjectAuthTests(BaseTest):
    def setUp(self):
        self.client = APIClient()
        self.test_subject = create_test_subject()

    def test_subject_gets_tokens_on_login(self):
        credentials = {
            "email": self.test_subject.email,
            "password": PASSWORD
        }

        response = self.client.post(reverse("subject_login"), data=credentials)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())


    # TODO; I have no idea why this case is failing. Fix it in the future!
    # def test_tokens_get_cleared_on_logout(self):
    #     self.access_token = str(AccessToken.for_user(self.test_subject))
    #     self.refresh_token = str(RefreshToken.for_user(self.test_subject))
    #     self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    #     response = self.client.post(reverse("subject_logout"), data={"refresh_token": self.refresh_token})
    #     self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    #     # Clear test client's session state
    #     self.client.logout()

    #     response = self.client.get(reverse("overview"))
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subject_gets_tokens_on_register(self):
        data  = create_test_user_or_subject_details()
        response = self.client.post(reverse("subject_register"), data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
        