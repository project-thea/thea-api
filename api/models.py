import uuid

from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(date_deleted__isnull=True, user_role=UserRole.ADMIN)

    def create_user(self, email, name, password=None, user_role=None):
        if not email:
            raise ValueError('Users must have an email address')
        
        user = self.model(email=self.normalize_email(email), name=name)
        user.set_password(password)
        
        if user_role:
            user.user_role = user_role

        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
class UserRole(models.TextChoices):
    LAB_TECHINICIAN = 'lab_tech', 'Lab_tech'
    USER = 'user', 'User'
    ADMIN = 'admin', 'Admin'
    SUBJECT = 'subject', 'Subject'
    
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    user_role= models.CharField(max_length=15, choices=UserRole.choices, default=UserRole.ADMIN)
    date_deleted = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def __str__(self):
        return self.name

class SubjectManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(date_deleted__isnull=True, user_role=UserRole.SUBJECT)

class Subject(User):
    objects = SubjectManager()

    class Meta:
        proxy = True

class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, null=True)
    date_deleted = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_location', null=True, blank=True)
    updated_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='updated_location',null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def __str__(self):
        return f"Location ({self.latitude}, {self.longitude})"
    
class Test(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, null=True)
    disease_id = models.ForeignKey('Disease', on_delete=models.CASCADE)
    date_deleted = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_test', null=True, blank=True)
    updated_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='updated_test', null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.disease_id}"
    
class Disease(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    date_deleted = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_diease', null=True, blank=True)
    updated_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='updated_disease', null=True, blank=True)

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
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, null=True)
    result_status = models.CharField(max_length=10, choices=RESULT_STATUS_CHOICES)
    test_id = models.ForeignKey('Test', on_delete=models.CASCADE)
    date_deleted = models.DateTimeField(null=True, blank=True)
    test_center = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_result', null=True, blank=True)
    updated_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='updated_result', null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def __str__(self):
        return f"Result for User ID {self.subject}: {self.result_status}"

class Hotspot(models.Model):    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    datetime = models.DateTimeField(null=True, blank=True)
    strength = models.IntegerField()
    date_deleted = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

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
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, null=True)
    date_deleted = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    # def __str__(self):
    #     return f"User ID {self.user_id} associated with Hotspot ID {self.hotspot_id}"
    
class InfectionRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotspot = models.ForeignKey('Hotspot', on_delete=models.CASCADE)
    date = models.DateField()
    num_of_drivers_exposed = models.IntegerField()
    num_of_drivers_infected = models.IntegerField()
    transmission_rate = models.DecimalField(max_digits=5, decimal_places=4)
    date_deleted = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        self.save()

    def __str__(self):
        return (f"Infection Rate at Hotspot ID {self.hotspot_id} on {self.date}: "
                f"{self.transmission_rate} with {self.num_of_drivers_infected} infected "
                f"out of {self.num_of_drivers_exposed} exposed")
