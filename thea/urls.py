from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenRefreshView

from api.views import LogoutView, RegisterView, TheaTokenObtainPairView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('api.urls')),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', TheaTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # client must pass the refresh token!
    path('logout/', LogoutView.as_view(), name='auth_logout')
]
