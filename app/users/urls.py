from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'register', UserRegister, basename='register')
router.register(r'raiting', IncreaseUserRatingView, basename='raiting')

urlpatterns = [
    path('refresh/', TokenRefreshView.as_view(), name="api_user_refresh"),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('categories/', CategoryListView.as_view(), name='categories'), 
    path('', include(router.urls)),
    path('send-confirmation/', SendEmailConfirmationView.as_view(), name='send-email-confirmation'),
    path('password-reset/send-code/', SendPasswordResetCodeView.as_view(), name='password-reset-send-code'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('cabinet/', UserCabinetView.as_view(), name='user-cabinet'),
]
