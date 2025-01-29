from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken

from ..models import User, Location, UserRole

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
