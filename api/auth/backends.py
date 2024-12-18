from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import PermissionDenied

from api.models import User, Subject
class TheaUserAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user_role = request.user_role
            user = User.objects.get(email=email, user_role=user_role)
            if user.check_password(password):
                return user
            else:
                raise PermissionDenied("Invalid credentials")
        except User.DoesNotExist:
            return None
        
    def get_user(self, id):
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None

def custom_user_auth_rule(user):
    return user is not None and user.date_deleted is None

class TheaSubjectAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user_role = request.user_role
            subject = Subject.objects.get(email=email, user_role=user_role)
            if subject.check_password(password):
                return subject
            else:
                raise PermissionDenied("Invalid credentials")
        except Subject.DoesNotExist:
            return None
        
    def get_user(self, id):
        try:
            return Subject.objects.get(pk=id)
        except Subject.DoesNotExist:
            return None