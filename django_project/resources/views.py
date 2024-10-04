from rest_framework import viewsets
from .models import Resource
from rest_framework.decorators import action
from .serializers import ResourceSerializer
from .permissions import IsAdminOrTeacherOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacherOrReadOnly]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'courses', 'uploaded_by'] 
    search_fields = ['category', 'tags', 'file'] 
    ordering_fields = ['category', 'file']  
    ordering = ['category']
    
    def get_queryset(self):
        """
        This view should return a list of all the resources for
        the currently authenticated user if they are a student.
        If they are a teacher or admin, return all resources.
        """
        user = self.request.user
        if user.role == 'student':
            return Resource.objects.filter(courses__students=user).distinct() 
        return Resource.objects.all() 

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


    @action(detail=False, methods=['get'])
    def by_course(self, request):
        course_id = request.query_params.get('course_id')
        resources = self.queryset.filter(courses_id=course_id)
        serializer = self.get_serializer(resources, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        resource = get_object_or_404(Resource, pk=pk)
        response = FileResponse(resource.file.open(), as_attachment=True)
        return response

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        resource = get_object_or_404(Resource, pk=pk)
        email = request.data.get('email')

        if not email:
            return Response({"detail": "Email field is required."}, status=status.HTTP_400_BAD_REQUEST)

        subject = f"Check out this resource: {resource.file.name}"
        message = f"Here is the link to download the resource: {request.build_absolute_uri(resource.file.url)}"
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        return Response({"detail": "Resource shared successfully."}, status=status.HTTP_200_OK)


