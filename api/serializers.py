from rest_framework import serializers
from .models import User, Location

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