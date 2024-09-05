from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import User

class UserTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(id="1b0a407b-f659-4f29-9cd1-5949b46392c9", name='jane doe', email="jane@doe.com", password='password')
        cls.user2 = User.objects.create(id="2b0a407b-f659-4f29-9cd1-5949b46392c9", name='john doe', email="john@doe.com", password='password')
        cls.user3 = User.objects.create(id="3b0a407b-f659-4f29-9cd1-5949b46392c9", name='jill doe', email="jill@doe.com", password='password')
        cls.user4 = User.objects.create(id="4b0a407b-f659-4f29-9cd1-5949b46392c9", name='jack doe', email="jack@doe.com", password='password', date_deleted="2021-01-01T00:00:00Z")

    def setUp(self):
        self.client = APIClient()

    def test_get_all_users(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_create_user(self):
        response = self.client.post('/api/users/', {'name': 'newuser', 'email': 'newuser@example.com', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_user(self):
        url = f'/api/users/{self.user3.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_user(self):
        data= {'email': 'jilk@doe.com'}
        url = f'/api/users/{self.user3.id}/'
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user3.refresh_from_db()

        self.assertEqual(self.user3.name, 'jill doe')
        self.assertEqual(self.user3.email, 'jilk@doe.com')

    