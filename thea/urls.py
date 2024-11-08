from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenRefreshView

from api.views import (
    SubjectRegisterView, 
    TheaSubjectTokenObtainPairView, 
    LogoutView, 
    UserRegisterView, 
    TheaUserTokenObtainPairView,
    LogoutView
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('api.urls')),

    path('register/user/', UserRegisterView.as_view(), name='user_register'),
    path('login/user/', TheaUserTokenObtainPairView.as_view(), name='user_token_obtain_pair'),
    path('login/user/refresh/', TokenRefreshView.as_view(), name='user_token_refresh'),
    path('logout/user/', LogoutView.as_view(), name='user_logout'),

    path('register/subject/', SubjectRegisterView.as_view(), name='subject_register'),
    path('login/subject/', TheaSubjectTokenObtainPairView.as_view(), name='subject_token_obtain_pair'),
    path('login/subject/refresh/', TokenRefreshView.as_view(), name='subject_token_refresh'),
    path('logout/subject/', LogoutView.as_view(), name='subject_logout')
]
