from rest_framework import viewsets,  status
from rest_framework.response import Response
from .models import Profile, Follow, Connection, FriendRequest
from .serializers import ProfileSerializer, FollowSerializer, ConnectionSerializer, FriendRequestSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from courses.models import Course
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['user__username', 'user__role']  
    search_fields = ['bio', 'interests', 'skills', 'user__username']  
    ordering_fields = ['user__username']  
    ordering = ['user__username']
    

    def get_queryset(self):
        user = self.request.user

        if user.role == 'teacher':
            courses = Course.objects.filter(teachers=user)
            students = Profile.objects.filter(user__enrolled_courses__in=courses, user__role='student')
            return Profile.objects.filter(Q(user=user) | Q(id__in=students.values_list('id', flat=True)))

        if user.role == 'student':
            courses = user.enrolled_courses.all()
            teachers = Profile.objects.filter(user__courses_taught__in=courses, user__role='teacher')
            return Profile.objects.filter(Q(user=user) | Q(id__in=teachers.values_list('id', flat=True)))

        if user.role == 'admin':
            return Profile.objects.all()
        return Profile.objects.none()

class FollowViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    filterset_fields = ['follower__username', 'followed__username']  
    search_fields = ['follower__username', 'followed__username']  

    def create(self, request):
        serializer = FollowSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(follower=request.user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            follow = Follow.objects.get(pk=pk, follower=request.user)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        follows = Follow.objects.filter(follower=request.user)
        serializer = FollowSerializer(follows, many=True)
        return Response(serializer.data)
    
class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    filterset_fields = ['from_user__username', 'to_user__username', 'accepted']  
    search_fields = ['from_user__username', 'to_user__username']  

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(to_user=user) | FriendRequest.objects.filter(from_user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    def update(self, request, pk=None):
        try:
            friend_request = self.get_object()
        except FriendRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if friend_request.to_user != request.user:
            return Response({"detail": "You cannot accept this friend request."}, status=status.HTTP_403_FORBIDDEN)

        if 'accepted' in request.data and request.data['accepted'] is True:

            friend_request.accepted = True
            friend_request.save()

            Connection.objects.create(user1=friend_request.from_user, user2=friend_request.to_user)
            Connection.objects.create(user1=friend_request.to_user, user2=friend_request.from_user)

            return Response({"detail": "Friend request accepted."}, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)

class ConnectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    filterset_fields = ['user1__username', 'user2__username']  
    search_fields = ['user1__username', 'user2__username']  

    def get_queryset(self):
        user = self.request.user
        return Connection.objects.filter(user1=user)