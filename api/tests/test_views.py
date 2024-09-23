from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from rest_framework_simplejwt.tokens import AccessToken

from ..models import User, Location, Disease, Test, Hotspot, Result, HotspotUserMap, InfectionRate

class BaseTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.user1 = User.objects.create(id="1b0a407b-f659-4f29-9cd1-5949b46392c9", name='jane doe', email="jane@doe.com", password='password')
        cls.user2 = User.objects.create(id="2b0a407b-f659-4f29-9cd1-5949b46392c9", name='john doe', email="john@doe.com", password='password')
        cls.user3 = User.objects.create(id="3b0a407b-f659-4f29-9cd1-5949b46392c9", name='jill doe', email="jill@doe.com", password='password')
        cls.user4 = User.objects.create(id="4b0a407b-f659-4f29-9cd1-5949b46392c9", name='jack doe', email="jack@doe.com", password='password', date_deleted="2021-01-01T00:00:00Z")

        cls.location1 = Location.objects.create(latitude=1.0, longitude=2.0, user=cls.user1)
        cls.location2 = Location.objects.create(latitude=3.0, longitude=5.0, user=cls.user1)
        cls.location3 = Location.objects.create(latitude=6.0, longitude=7.0, user=cls.user2)
        cls.location4 = Location.objects.create(latitude=8.0, longitude=9.0, user=cls.user2)

        cls.disease1 = Disease.objects.create(name='COVID-19')
        cls.disease2 = Disease.objects.create(name='Malaria')
        cls.disease3 = Disease.objects.create(name='Monkey Pox')

        cls.test1 = Test.objects.create(user=cls.user1, disease_id=cls.disease1)
        cls.test2 = Test.objects.create(user=cls.user1, disease_id=cls.disease1)
        cls.test3 = Test.objects.create(user=cls.user2, disease_id=cls.disease1)
        cls.test4 = Test.objects.create(user=cls.user3, disease_id=cls.disease1)

        cls.result1 = Result.objects.create(user=cls.user1, result_status='positive', test_id=cls.test1, test_center='LUTH')
        cls.result1 = Result.objects.create(user=cls.user1, result_status='positive', test_id=cls.test2, test_center='LUTH')

        cls.hotspot1 = Hotspot.objects.create(latitude=1.0, longitude=2.0, strength=5, datetime="2021-01-01T00:00:00Z")
        cls.hotspot2 = Hotspot.objects.create(latitude=3.0, longitude=5.0, strength=3, datetime="2021-01-01T00:00:00Z")
        cls.hotspot3 = Hotspot.objects.create(latitude=6.0, longitude=7.0, strength=2, datetime="2021-01-01T00:00:00Z")

        cls.hotspot_user_map1 = HotspotUserMap.objects.create(user=cls.user1, hotspot=cls.hotspot1)
        cls.hotspot_user_map2 = HotspotUserMap.objects.create(user=cls.user1, hotspot=cls.hotspot2)
        cls.hotspot_user_map3 = HotspotUserMap.objects.create(user=cls.user2, hotspot=cls.hotspot3)

        cls.infection_rate1 = InfectionRate.objects.create(hotspot=cls.hotspot1, date="2021-01-01", num_of_drivers_exposed=10, num_of_drivers_infected=5, transmission_rate=0.5)
        cls.infection_rate2 = InfectionRate.objects.create(hotspot=cls.hotspot1, date="2021-01-01", num_of_drivers_exposed=10, num_of_drivers_infected=3, transmission_rate=0.3)
        cls.infection_rate3 = InfectionRate.objects.create(hotspot=cls.hotspot2, date="2021-01-01", num_of_drivers_exposed=10, num_of_drivers_infected=2, transmission_rate=0.2)

        access_token = AccessToken.for_user(cls.user1)
        cls.access_token = str(access_token)
    
    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

# class UserTests(BaseTest):
#     def test_get_all_users(self):
#         response = self.client.get('/api/users/')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 3)

#     def test_create_user(self):
#         response = self.client.post('/api/users/', {'name': 'newuser', 'email': 'newuser@example.com', 'password': 'password123'})
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_delete_user(self):
#         url = f'/api/users/{self.user3.id}/'
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     def test_update_user(self):
        # data= {'email': 'jilk@doe.com'}
        # url = f'/api/users/{self.user3.id}/'
        # response = self.client.patch(url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # self.user3.refresh_from_db()

        # self.assertEqual(self.user3.name, 'jill doe')
        # self.assertEqual(self.user3.email, 'jilk@doe.com')

class LocationTests(BaseTest):
    def test_get_all_locations(self):
        response = self.client.get(f'/api/locations/?user={self.user1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_location(self):
        data = {
            "locations": [
                {'latitude': 1.0, 'longitude': 2.0, 'user': self.user1.id},
                {'latitude': 3.0, 'longitude': 4.0, 'user': self.user1.id}
            ]
        }
        response = self.client.post('/api/locations/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class DiseaseTests(BaseTest):
    def test_get_all_diseases(self):
        response = self.client.get('/api/diseases/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_create_disease(self):
        response = self.client.post('/api/diseases/', {'name': 'Ebola'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_disease(self):
        url = f'/api/diseases/{self.disease3.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_disease(self):
        data= {'name': 'Monkey Pox'}
        url = f'/api/diseases/{self.disease3.id}/'
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.disease3.refresh_from_db()

        self.assertEqual(self.disease3.name, 'Monkey Pox')

class TestTests(BaseTest):
    def test_get_all_tests(self):
        response = self.client.get('/api/tests/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(f'/api/tests/?user={self.user1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_test(self):
        response = self.client.post('/api/tests/', {'user': self.user1.id, 'disease_id': self.disease1.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_delete_test(self):
        url = f'/api/tests/{self.test4.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_update_test(self):
        data= {'disease_id': self.disease2.id}
        url = f'/api/tests/{self.test4.id}/'
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.test4.refresh_from_db()

        self.assertEqual(self.test4.disease_id, self.disease2)

class ResultTests(BaseTest):
    def test_get_all_results(self):
        response = self.client.get('/api/results/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(f'/api/results/?user={self.user1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    # what's happening here????? 
    # def test_create_result(self):
    #     response = self.client.post('/api/results/', {'user': self.user1.id, 'result_status': 'positive', 'test_id': self.test2.id, 'test_center': 'LUTH'})
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_delete_result(self):
        url = f'/api/results/{self.result1.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_update_result(self):
        data= {'result_status': 'negative'}
        url = f'/api/results/{self.result1.id}/'
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.result1.refresh_from_db()

        self.assertEqual(self.result1.result_status, 'negative')

class HotspotTests(BaseTest):
    def test_get_all_hotspots(self):
        response = self.client.get('/api/hotspots/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_create_hotspot(self):
        response = self.client.post('/api/hotspots/', {'latitude': 1.0, 'longitude': 2.0, 'strength': 5})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_delete_hotspot(self):
        url = f'/api/hotspots/{self.hotspot3.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_update_hotspot(self):
        data= {'strength': 10}
        url = f'/api/hotspots/{self.hotspot3.id}/'
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.hotspot3.refresh_from_db()

        self.assertEqual(self.hotspot3.strength, 10)

class InfectionRateTests(BaseTest):
    def test_get_all_infection_rates(self):
        response = self.client.get('/api/infection-rates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_create_infection_rate(self):
        response = self.client.post('/api/infection-rates/', {'hotspot': self.hotspot1.id, 'date': '2021-01-01', 'num_of_drivers_exposed': 10, 'num_of_drivers_infected': 5, 'transmission_rate': 0.5})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)