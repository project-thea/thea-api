from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status

from . import BaseTest

class UserTests(BaseTest):
    def test_create_user(self):
        payload = {'name': 'newuser', 'email': 'newuser@example.com', 'password': 'password123'}
        response = self.client.post(reverse("user_register"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        User = get_user_model()
        self.assertTrue(User.objects.filter(email=payload['email']).exists())

        # Test required fields are missing
        bad_payload = {"name": "testuser"} 
        response = self.client.post(reverse("user_register"), bad_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

         # Test duplicate email
        response = self.client.post(reverse("user_register"), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
