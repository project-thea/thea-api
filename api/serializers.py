from rest_framework import serializers
from .models import Subject, User, Location, Test, Disease, Result, Hotspot, InfectionRate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'user_role']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def get():
        pass

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user
    
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'email', 'password', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def get():
        pass

    def create(self, validated_data):
        subject = Subject.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return subject
    
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['latitude', 'longitude', 'user']

class BulkLocationSerializer(serializers.Serializer):
    locations = LocationSerializer(many=True)

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['user', 'disease_id']

class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = ['name']

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['user', 'result_status', 'test_center']

class HotspotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotspot
        fields = ['latitude', 'longitude', 'datetime', 'strength']

    def create(self, validated_data):
        hotspot = Hotspot(
            latitude=validated_data['latitude'],
            longitude=validated_data['longitude'],
            strength=validated_data['strength']
        )
        hotspot.set_datetime()
        hotspot.save()
        return hotspot

class InfectionRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfectionRate
        fields = ['hotspot', 'date', 'num_of_drivers_exposed', 'num_of_drivers_infected', 'transmission_rate']