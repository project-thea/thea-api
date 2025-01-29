from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  LocationViewSet, TestViewSet, DiseaseViewSet, ResultViewSet, HotspotViewSet, InfectionRateViewSet, SubjectViewSet, OverviewView

router = DefaultRouter()
# router.register(r'users', UserViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'tests', TestViewSet)
router.register(r'diseases', DiseaseViewSet)
router.register(r'results', ResultViewSet)
router.register(r'hotspots', HotspotViewSet)
router.register(r'infection-rates', InfectionRateViewSet)
router.register(r'subjects', SubjectViewSet)

urlpatterns = [
    path('', include(router.urls), name='api'),
    path('overview/', OverviewView.as_view(), name='overview')
]
