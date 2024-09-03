from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LocationViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'locations', LocationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
