import uuid

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.status import HTTP_100_CONTINUE
from rest_framework.test import APITestCase, APIClient

from rest_framework_simplejwt.tokens import AccessToken

from ..models import User, Location, Subject, UserRole
from ..serializers import SubjectSerializer



class BaseTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        # create some sample users
        cls.user1 = User.objects.create(id="1b0a407b-f659-4f29-9cd1-5949b46392c9", name='jane user', email="jane@user.com", password='password')
        cls.user2 = User.objects.create(id="2b0a407b-f659-4f29-9cd1-5949b46392c9", name='john user', email="john@user.com", password='password')
        cls.user3 = User.objects.create(id="3b0a407b-f659-4f29-9cd1-5949b46392c9", name='jill user', email="jill@user.com", password='password')
        cls.user4 = User.objects.create(id="4b0a407b-f659-4f29-9cd1-5949b46392c9", name='jack user', email="jack@user.com", password='password', date_deleted="2021-01-01T00:00:00Z")

        # create some sample subjects
        cls.subject1 = User.objects.create(user_role=UserRole.SUBJECT, id="5b0a407b-f659-4f29-9cd1-5949b46392c9", name='jane subject', email="jane@subject.com", password='password')
        cls.subject2 = User.objects.create(user_role=UserRole.SUBJECT, id="6b0a407b-f659-4f29-9cd1-5949b46392c9", name='john subject', email="john@subject.com", password='password')
        cls.subject3 = User.objects.create(user_role=UserRole.SUBJECT, id="7b0a407b-f659-4f29-9cd1-5949b46392c9", name='jill subject', email="jill@subject.com", password='password')
        cls.subject4 = User.objects.create(user_role=UserRole.SUBJECT, id="8b0a407b-f659-4f29-9cd1-5949b46392c9", name='jack subject', email="jack@subject.com", password='password', date_deleted="2021-01-01T00:00:00Z")

        cls.location1 = Location.objects.create(latitude=1.0, longitude=2.0, subject=cls.subject1)
        cls.location2 = Location.objects.create(latitude=3.0, longitude=5.0, subject=cls.subject1)
        cls.location3 = Location.objects.create(latitude=6.0, longitude=7.0, subject=cls.subject2)
        cls.location4 = Location.objects.create(latitude=8.0, longitude=9.0, subject=cls.subject2)

        access_token = AccessToken.for_user(cls.user1)
        cls.access_token = str(access_token)
    
    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

class UserTests(BaseTest):
    def test_create_user(self):
        payload = {'name': 'newuser', 'email': 'newuser@example.com', 'password': 'password123'}
        response = self.client.post('/register/user/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        User = get_user_model()
        self.assertTrue(User.objects.filter(email=payload['email']).exists())

        # Test required fields are missing
        bad_payload = {"name": "testuser"} 
        response = self.client.post('/register/user/', bad_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

         # Test duplicate email
        response = self.client.post('/register/user/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class LocationTests(BaseTest):
    def test_get_all_locations(self):
        response = self.client.get(f'/api/locations/?subject={self.subject1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # should specify a subject id when fetching locations
        response = self.client.get(f'/api/locations/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_location(self):
        data = {
            "locations": [
                {'latitude': 1.0, 'longitude': 2.0, 'subject': self.subject1.id},
                {'latitude': 3.0, 'longitude': 4.0, 'subject': self.subject1.id}
            ]
        }
        response = self.client.post('/api/locations/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class OverviewTests(BaseTest):
    def test_get_overview(self):
        response = self.client.get(f'/api/overview/')
        data = response.json()

        top_level_fields = ['num_subjects', 'num_tests', 'num_users', 'weekly_stats', 'num_diseases']
        for field in top_level_fields:
            self.assertIn(field, data)

        self.assertEqual(len(data["weekly_stats"]), 7)
