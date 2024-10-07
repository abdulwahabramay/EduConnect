from django.urls import path,  include
from .views import CustomUserRegistrationView, AuthViewSet, PasswordResetRequestView, PasswordResetConfirmView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')



urlpatterns = [
    path('', include(router.urls)),
    path('register/', CustomUserRegistrationView.as_view({'post': 'create'}), name='register'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
]
