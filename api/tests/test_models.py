from django.test import TestCase
from ..models import User, Location, Disease, Test, Hotspot, Result, HotspotUserMap, InfectionRate

class TestModels(TestCase):
    def test_soft_delete_user_model(self):
        user = User.objects.create(id="1b0a407b-f659-4f29-9cd1-5949b46392c9", name='jane doe', email="jane@doe.com", password='password')
        user.delete()
        self.assertIsNotNone(user.date_deleted)