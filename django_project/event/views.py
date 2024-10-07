from rest_framework import viewsets, permissions
from .models import Event
from .serializers import EventSerializer
from django.core.mail import send_mail
from django.conf import settings
from courses.models import Course
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['course', 'created_by', 'date'] 
    search_fields = ['title', 'description']

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        select_all_students = self.request.data.get('select_all_students', False)

        if select_all_students:
            students = course.students.all()
            event = serializer.save(created_by=self.request.user)
            event.students.set(students) 
            self.send_event_emails(event) 
        else:
            students = self.request.data.get('students', [])
            if not students:
                raise serializers.ValidationError({'students': 'This field is required when select_all_students is false.'})
            student_objects = CustomUser.objects.filter(id__in=students, role='student')
            if not student_objects.exists():
                raise serializers.ValidationError({'students': 'No valid student IDs provided.'})
            event = serializer.save(created_by=self.request.user)
            event.students.set(student_objects) 
            self.send_event_emails(event) 

    def send_event_emails(self, event):
        student_emails = event.students.values_list('email', flat=True)
        subject = f"New Event Created: {event.title}"
        message = f"You have been invited to the following event:\n\n" \
                  f"Title: {event.title}\n" \
                  f"Description: {event.description}\n" \
                  f"Date: {event.date}\n" \
                  f"Course: {event.course.name}\n\n" \
                  f"Please check your course dashboard for more details."

        for email in student_emails:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

