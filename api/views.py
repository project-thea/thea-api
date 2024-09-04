from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import User, Location, Test, Disease, Result, Hotspot, InfectionRate
from .serializers import UserSerializer, LocationSerializer, BulkLocationSerializer, TestSerializer, DiseaseSerializer, HotspotSerializer, ResultSerializer, InfectionRateSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(date_deleted__isnull=True)
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.date_deleted = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.filter(date_deleted__isnull=True)
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        serializer = BulkLocationSerializer(data=request.data)
        if serializer.is_valid():
            locations_data = serializer.validated_data['locations']
            Location.objects.bulk_create(
                [Location(**data) for data in locations_data]
            )
            return Response({'status': 'locations created'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.date_deleted = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.filter(date_deleted__isnull=True)
    serializer_class = TestSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.date_deleted = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DiseaseViewSet(viewsets.ModelViewSet):
    queryset = Disease.objects.filter(date_deleted__isnull=True)
    serializer_class = DiseaseSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.date_deleted = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.filter(date_deleted__isnull=True)
    serializer_class = ResultSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.date_deleted = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class HotspotViewSet(viewsets.ModelViewSet):
    queryset = Hotspot.objects.filter(date_deleted__isnull=True)
    serializer_class = HotspotSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.date_deleted = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class InfectionRateViewSet(viewsets.ModelViewSet):
    queryset = InfectionRate.objects.filter(date_deleted__isnull=True)
    serializer_class = InfectionRateSerializer
    http_method_names = ['get']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.date_deleted = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)