from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  LocationViewSet, TestViewSet, DiseaseViewSet, ResultViewSet, HotspotViewSet, InfectionRateViewSet

router = DefaultRouter()
# router.register(r'users', UserViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'tests', TestViewSet)
router.register(r'diseases', DiseaseViewSet)
router.register(r'results', ResultViewSet)
router.register(r'hotspots', HotspotViewSet)
router.register(r'infection-rates', InfectionRateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
