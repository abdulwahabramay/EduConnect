from rest_framework import routers
from .views import UserViewSet
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('gettoken/', obtain_auth_token )
]