from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet , FollowViewSet, ConnectionViewSet, FriendRequestViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'follows', FollowViewSet, basename='follow')
router.register(r'connections', ConnectionViewSet)
router.register(r'friend-requests', FriendRequestViewSet, basename='friend-request')

urlpatterns = [
    path('', include(router.urls)),
    path('friend-requests/<int:pk>/accept/', FriendRequestViewSet.as_view({'post': 'accept'})),
]