from rest_framework import serializers
from .models import User, Location, Test, Disease, Result, Hotspot, InfectionRate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User(
            name=validated_data['name'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
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