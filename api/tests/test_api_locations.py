from django.urls import reverse

from rest_framework import status

from . import BaseTest

class LocationTests(BaseTest):
    def test_get_all_locations(self):
        response = self.client.get(reverse("location-list"), data={"subject": self.subject1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # should specify a subject id when fetching locations
        response = self.client.get(reverse("location-list"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_location(self):
        data = {
            "locations": [
                {'latitude': 1.0, 'longitude': 2.0, 'subject': self.subject1.id},
                {'latitude': 3.0, 'longitude': 4.0, 'subject': self.subject1.id}
            ]
        }
        response = self.client.post(reverse("location-list"), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

