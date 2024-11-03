from django.utils import timezone
from django.db.models import F
from django.core.paginator import Paginator

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Subject, User, Location, Test, Disease, Result, Hotspot, InfectionRate
from .serializers import (
    SubjectSerializer,
    UserSerializer,
    LocationSerializer,
    BulkLocationSerializer,
    TestSerializer,
    DiseaseSerializer,
    HotspotSerializer,
    ResultSerializer,
    InfectionRateSerializer
)
class TheaUserTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom claims...
        data['user'] = UserSerializer(self.user).data
        return data

class TheaUserTokenObtainPairView(TokenObtainPairView):
    serializer_class = TheaUserTokenObtainPairSerializer

class TheaSubjectTokenObtainPairSerializer(TokenObtainPairSerializer):
    # TODO; this is not authenticating well at the moment since all the requests
    # seem to be routed to the User model. Come back to this later!
    def validate(self, attrs):
        data = super().validate(attrs)
        
        data['subject'] = SubjectSerializer(self.user).data
        return data

class TheaSubjectTokenObtainPairView(TokenObtainPairView):
    serializer_class = TheaSubjectTokenObtainPairSerializer

class UserRegisterView(APIView):
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

class SubjectRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            subject = serializer.save()
            refresh = RefreshToken.for_user(subject)
            return Response({
                'subject': SubjectSerializer(subject).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    # i think this view could work for both users and subjects!

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            outstanding_token = OutstandingToken.objects.get(token=token)
            BlacklistedToken.objects.create(token=outstanding_token)
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.filter(date_deleted__isnull=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        subject_tests =  Test.objects.filter(subject_id=instance.id).annotate(
            test_id=F('id'),
            test_date=F('created_at'),
            test_subject=F('subject__name'),
            disease=F('disease_id__name'),     
            test_result=F('result__result_status'),
            test_center=F('result__test_center')
        ).values(
            'test_id',
            'test_date',
            'test_subject',
            'disease',
            'test_result',
            'test_center'
        )
        
        serializer = self.get_serializer(instance)
        custom_data = serializer.data
        custom_data['tests'] = subject_tests

        return Response(custom_data)

    def list(self, request):
        queryset = self.get_queryset()

        name_filter = request.query_params.get('name')
        if name_filter:
            name_filter = name_filter.rstrip('/')
            queryset = self.queryset.filter(name__icontains=name_filter)

        total = queryset.count()
        serializer = SubjectSerializer(queryset, many=True)

        return Response({
            'total': total,
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.date_deleted = timezone.now()
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
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

class OverviewView(APIView):
    def get(self, request):
        stats = [{
            'num_subjects': Subject.objects.filter(date_deleted__isnull=True).count(),
            'num_tests': Test.objects.count(),
            'num_diseases': Disease.objects.count(),
            'num_users': User.objects.filter(date_deleted__isnull=True).count()
        }]

        return Response(stats)

class TheaPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = '_end'
    page_query_param = '_start'

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.filter(date_deleted__isnull=True).select_related('subject', 'disease', 'result')
    serializer_class = TestSerializer
    pagination_class = TheaPagination

    def list(self, request, *args, **kwargs):
        _start = request.query_params.get('_start')
        _end = request.query_params.get('_end')

        # TODO; this query is not doing what i want at the moment - it is
        # just returning all the records in the tests table
        queryset = self.get_queryset().annotate(
            test_id=F('id'),
            test_date=F('created_at'),
            test_subject=F('subject__name'),
            disease=F('disease_id__name'),
            test_result=F('result__result_status'),
            test_center=F('result__test_center')
        ).values('test_id', 'test_date', 'test_subject', 'disease', 'test_result', 'test_center').order_by('created_at')

        if _start and _end:
            _start = int(_start)
            _end = int(_end.rstrip('/'))

            paginator = Paginator(queryset, _end - _start)
            page_number = (_start // (_end  - _start)) + 1
            page = paginator.get_page(page_number)

            return Response({
                'total': len(list(page)),
                'data': list(page)
            })
        else:
            page = self.paginate_queryset(queryset)
            return Response({
                'total': len(list(page)),
                'data': list(page)
            })

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