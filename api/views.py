import json
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Location, Test, Disease, Result, Hotspot, InfectionRate
from .serializers import UserSerializer, LocationSerializer, BulkLocationSerializer, TestSerializer, DiseaseSerializer, HotspotSerializer, ResultSerializer, InfectionRateSerializer


class TheaTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add any other custom claims you want
        data['user'] = UserSerializer(self.user).data        
        return data

class TheaTokenObtainPairView(TokenObtainPairView):
    serializer_class = TheaTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            outstanding_token = OutstandingToken.objects.get(token=token)
            BlacklistedToken.objects.create(token=outstanding_token)
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# Is this needed???????
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.filter(date_deleted__isnull=True)
#     serializer_class = UserSerializer

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.date_deleted = timezone.now()
#         instance.save()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.filter(date_deleted__isnull=True)
    serializer_class = LocationSerializer
    http_method_names = ['get', 'post']

    def list(self, request, *args, **kwargs):
        # get locations that a particular user has been to
        user = request.query_params.get('user')
        if user:
            queryset = Location.objects.filter(date_deleted__isnull=True, user_id=user)
        else:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LocationSerializer(queryset, many=True)
        return Response(serializer.data)

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

    def list(self, request, *args, **kwargs):
        user = request.query_params.get('user')
        if user:
            queryset = Test.objects.filter(date_deleted__isnull=True, user_id=user)
        else:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TestSerializer(queryset, many=True)
        return Response(serializer.data)

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

    def list(self, request, *args, **kwargs):
        user = request.query_params.get('user')
        if user:
            queryset = Result.objects.filter(date_deleted__isnull=True, user_id=user)
        else:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ResultSerializer(queryset, many=True)
        return Response(serializer.data)


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