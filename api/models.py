import uuid

from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.utils import timezone

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    date_deleted = models.DateTimeField(null=True, blank=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def __str__(self):
        return self.name

class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    date_deleted = models.DateTimeField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def __str__(self):
        return f"Location ({self.latitude}, {self.longitude})"
    
class Test(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    disease_id = models.ForeignKey('Disease', on_delete=models.CASCADE)
    test_date = models.DateField()
    date_deleted = models.DateTimeField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def __str__(self):
        return f"Test for Disease ID {self.disease_id} on {self.test_date}"
    
class Disease(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    date_deleted = models.DateTimeField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def __str__(self):
        return self.name

class Result(models.Model):
    RESULT_STATUS_CHOICES = [
        ('negative', 'Negative'),
        ('positive', 'Positive'),
        ('undefined', 'Undefined'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    result_status = models.CharField(max_length=10, choices=RESULT_STATUS_CHOICES)
    test_date = models.DateField()
    date_deleted = models.DateTimeField(null=True, blank=True)
    test_center = models.CharField(max_length=255)

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def __str__(self):
        return f"Result for User ID {self.user_id} on {self.test_date}: {self.result_status}"

class Hotspot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    datetime = models.DateTimeField(null=True, blank=True)
    strength = models.IntegerField()
    date_deleted = models.DateTimeField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def set_datetime(self):
        self.datetime = timezone.now()

    def __str__(self):
        return f"Hotspot at ({self.latitude}, {self.longitude}) on {self.datetime} with strength {self.strength}"
    
class HotspotUserMap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotspot = models.ForeignKey('Hotspot', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    date_deleted = models.DateTimeField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def __str__(self):
        return f"User ID {self.user_id} associated with Hotspot ID {self.hotspot_id}"
    
class InfectionRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotspot = models.ForeignKey('Hotspot', on_delete=models.CASCADE)
    date = models.DateField()
    num_of_drivers_exposed = models.IntegerField()
    num_of_drivers_infected = models.IntegerField()
    transmission_rate = models.DecimalField(max_digits=5, decimal_places=4)
    date_deleted = models.DateTimeField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def __str__(self):
        return (f"Infection Rate at Hotspot ID {self.hotspot_id} on {self.date}: "
                f"{self.transmission_rate} with {self.num_of_drivers_infected} infected "
                f"out of {self.num_of_drivers_exposed} exposed")
