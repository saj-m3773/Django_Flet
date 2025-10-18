from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, CustomTokenObtainPairView, PasswordResetRequestView, PasswordResetConfirmView, \
    ProfileView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('forgot-password/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path("profile/", ProfileView.as_view(), name="user-profile"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
