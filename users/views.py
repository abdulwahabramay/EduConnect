from rest_framework import viewsets
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import CustomUserPermission
from courses.models import Course
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [CustomUserPermission]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email']
    ordering_fields = ['date_joined', 'username']
    ordering = ['-date_joined']

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            return CustomUser.objects.all()

        if user.role == 'teacher':
            courses = user.courses_taught.all()
            students = CustomUser.objects.filter(enrolled_courses__in=courses, role='student')
            return CustomUser.objects.filter(
                Q(id=user.id) | Q(id__in=students.values_list('id', flat=True))
            ).distinct()

        if user.role == 'student':
            courses = user.enrolled_courses.all() 
            teachers = CustomUser.objects.filter(courses_taught__in=courses, role='teacher')

            return CustomUser.objects.filter(
                Q(id=user.id) | Q(id__in=teachers.values_list('id', flat=True))
            ).distinct()

        return CustomUser.objects.none()

