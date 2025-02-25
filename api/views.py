from datetime import timedelta

from django.utils import timezone
from django.db.models import F, Subquery, OuterRef, Count, Q
from django.core.paginator import Paginator
from django.db.models.functions import TruncDate, Coalesce

from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from rest_framework_simplejwt.tokens import RefreshToken, Token
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import (
    Subject,
    User,
    Location,
    Test,
    Disease,
    Result,
    Hotspot,
    InfectionRate,
    UserRole,
    SnappedLocation
)

from .serializers import (
    SnappedLocationSerializer,
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
        self.context['request'].user_role = UserRole.ADMIN
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data

class TheaUserTokenObtainPairView(TokenObtainPairView):
    serializer_class = TheaUserTokenObtainPairSerializer
    
class TheaSubjectTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        self.context['request'].user_role = UserRole.SUBJECT
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
    queryset = Subject.objects.filter(date_deleted__isnull=True, user_role=UserRole.SUBJECT)

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
    
    def get_subjects_most_recent_locations_coarse(self, subject_id=None, start_date=None, end_date=None):
        # one of the reasons why i dont filter by date_deleted is that in the clients, i don't
        # see a scenario where we are deleting locations. in case that happens, then i will
        # update this method accordingly.
        if subject_id and start_date and end_date:
            # Get all locations for specific subject within date range
            locations = Location.objects.filter(
                subject_id=subject_id
            ).filter(
                Q(timestamp__isnull=False, timestamp__range=[start_date, end_date]) |
                Q(timestamp__isnull=True, created_at__range=[start_date, end_date])
            ).select_related('subject').order_by(
                Coalesce('timestamp', 'created_at')
            )
            return locations
        
        # Default behavior - get most recent location for each subject
        latest_datetime_subquery = Location.objects.filter(
            subject=OuterRef('subject')
        ).order_by(
            Coalesce('timestamp', 'created_at').desc()
        ).values(
            latest_datetime=Coalesce('timestamp', 'created_at')
        )[:1]

        latest_locations = Location.objects.filter(
            Q(timestamp__isnull=False, timestamp=Subquery(latest_datetime_subquery)) |
            Q(timestamp__isnull=True, created_at=Subquery(latest_datetime_subquery))
        ).select_related('subject')

        return latest_locations

    def get_subjects_most_recent_locations_snapped(self, subject_id=None, start_date=None, end_date=None):
        if subject_id and start_date and end_date:
            locations = (
                SnappedLocation.objects
                .select_related('original_location')
                .filter(
                    Q(original_location__timestamp__isnull=False, original_location__timestamp__range=[start_date, end_date]) | 
                    Q(original_location__timestamp__isnull=True, original_location__created_at__range=[start_date, end_date]),
                    original_location__subject=subject_id
                )
                .order_by(Coalesce('original_location__timestamp', 'original_location__created_at'))
            )

            return locations
            
        # Default behavior - get most recent snapped location for each subject
        most_recent_snapped = (
            SnappedLocation.objects
            .select_related('original_location__subject')
            .filter(
                original_location__id=Subquery(
                    Location.objects
                    .filter(subject=OuterRef('original_location__subject'))
                    .order_by(Coalesce('timestamp', 'created_at').desc())
                    .values('id')[:1]
                )
            )
        )

        return most_recent_snapped

    def get_subjects_most_recent_locations(self, type, subject_id=None, start_date=None, end_date=None):
        if type == 'coarse':
            return self.get_subjects_most_recent_locations_coarse(subject_id, start_date, end_date)
        
        return self.get_subjects_most_recent_locations_snapped(subject_id, start_date, end_date)
    
    @action(detail=False, methods=['get'], url_path='latest-locations')
    def get_subjects_recent_locations(self, request):
        subject_id = request.query_params.get('subject_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        locations_type = request.query_params.get('type')

        if not locations_type:
            locations_type = 'coarse'
            serializer = LocationSerializer
        else:
            serializer = SnappedLocationSerializer

        if subject_id and start_date and end_date:
            try:
                # If only date is provided, append default time
                if len(start_date) == 10:
                    start_date += ' 00:00:00'
                if len(end_date) == 10:
                    end_date += ' 23:59:59'
                
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
                locations = self.get_subjects_most_recent_locations(
                    type=locations_type,
                    subject_id=subject_id,
                    start_date=timezone.make_aware(start_date),
                    end_date=timezone.make_aware(end_date)
                )
            except ValueError as ve:
                return Response(
                    {
                        'status': 'error',
                        'code': 400,
                        'message': str(ve),
                        'timestamp': timezone.now().isoformat()
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            locations = self.get_subjects_most_recent_locations(type=locations_type)

        _serializer = serializer(locations, many=True)

        return Response({
            'total': locations.count(),
            'data': _serializer.data
        })
    
class LocationViewSet(viewsets.ModelViewSet):
    # TODO; remove this line since it is not secure
    permission_classes = [AllowAny]
    
    queryset = Location.objects.filter(date_deleted__isnull=True)
    serializer_class = LocationSerializer
    http_method_names = ['get', 'post']

    def list(self, request, *args, **kwargs):
        # get locations of a subject
        subject = request.query_params.get('subject')
        if subject:
            queryset = Location.objects.filter(date_deleted__isnull=True, subject=subject)
        else:
            return Response({'error': 'subject is required'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LocationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = BulkLocationSerializer(data=request.data)
        if serializer.is_valid():
            locations_data = serializer.validated_data['locations']

            if len(locations_data) == 0:
                return Response({'error': 'locations data is required'}, status=status.HTTP_400_BAD_REQUEST)
            
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
        today = timezone.now().date()
        week_ago = today - timedelta(days=6)

        # Get subjects count per day
        subjects_per_day = (
            Subject.objects
            .filter(created_at__date__gte=week_ago)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(subject_count=Count('id'))
            .order_by('date')
        )

        # Get tests count per day
        tests_per_day = (
            Test.objects
            .filter(created_at__date__gte=week_ago)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(test_count=Count('id'))
            .order_by('date')
        )

        # Create a list of all dates in the range
        date_range = [(today - timedelta(days=x)) for x in range(6, -1, -1)]

        # Convert querysets to dictionaries for easier lookup
        subjects_dict = {item['date']: item['subject_count'] for item in subjects_per_day}
        tests_dict = {item['date']: item['test_count'] for item in tests_per_day}

        # Combine the results
        weekly_stats = [
            {
                'date': date.strftime('%Y-%m-%d'),
                'day': date.strftime('%A'),
                'new_subjects': subjects_dict.get(date, 0),
                'tests_taken': tests_dict.get(date, 0)
            }
            for date in date_range
        ]    

        data = {
            'num_subjects': Subject.objects.filter(date_deleted__isnull=True).count(),
            'num_tests': Test.objects.count(),
            'num_diseases': Disease.objects.count(),
            'num_users': User.objects.filter(date_deleted__isnull=True).count(),
            'weekly_stats': weekly_stats
        }

        return Response(data)

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