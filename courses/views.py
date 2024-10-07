from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404

from .models import Course, EnrollmentRequest, CourseActivityLog
from .serializers import CourseSerializer
from .permissions import IsAdminOrReadOnly
from django.views.decorators.csrf import csrf_exempt

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]  
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['teachers', 'students']  
    search_fields = ['name', 'description']

    def perform_create(self, serializer):
        course = serializer.save(created_by=self.request.user)  # Save the course instance
        # Log the activity
        CourseActivityLog.objects.create(
            course=course,
            user=self.request.user,
            action='create'
        )
        
    def perform_update(self, serializer):
        course = serializer.save(created_by=self.request.user)  # Save the updated course instance
        # Log the activity
        CourseActivityLog.objects.create(
            course=course,
            user=self.request.user,
            action='update'
        )
        
    
    def perform_destroy(self, instance):
        # Log the activity before deleting the instance
        CourseActivityLog.objects.create(
            course=instance,
            user=self.request.user,
            action='delete'
        )
        instance.delete()

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def request_enrollment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.role == 'student':
        enrollment_request, created = EnrollmentRequest.objects.get_or_create(student=request.user, course=course)

        if created:
            return Response({"message": "Enrollment request submitted successfully!"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "You have already submitted an enrollment request for this course."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "Only students can request enrollment."}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def approve_enrollment(request, enrollment_request_id):
    enrollment_request = get_object_or_404(EnrollmentRequest, id=enrollment_request_id)
    if request.user.role != 'admin':
        return Response({"message": "Only admins can approve enrollment requests."}, status=status.HTTP_403_FORBIDDEN)
    enrollment_request.approved = True
    enrollment_request.status = 'approved' 
    enrollment_request.save()
    
    course = enrollment_request.course
    course.students.add(enrollment_request.student)

    return Response({"message": "Enrollment request approved successfully!"}, status=status.HTTP_200_OK)