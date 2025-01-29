from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status

from . import BaseTest

class OverviewTests(BaseTest):
    def test_get_overview(self):
        response = self.client.get(reverse('overview'))
        data = response.json()

        top_level_fields = ['num_subjects', 'num_tests', 'num_users', 'weekly_stats', 'num_diseases']
        for field in top_level_fields:
            self.assertIn(field, data)

        self.assertEqual(len(data["weekly_stats"]), 7)
