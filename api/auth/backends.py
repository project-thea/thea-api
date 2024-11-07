from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import PermissionDenied

from api.models import Subject

class SubjectAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            subject = Subject.objects.get(email=email)

            if subject:
                if subject.check_password(password):
                    return subject
                else:
                    raise PermissionDenied("Invalid credentials")    
        except Subject.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        try:
            return Subject.objects.get(pk=user_id)
        except Subject.DoesNotExist:
            return None