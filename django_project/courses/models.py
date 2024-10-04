from django.db import models
from django.conf import settings  

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='courses_taught', limit_choices_to={'role': 'teacher'}, blank=True, null=True )
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_courses', limit_choices_to={'role': 'student'}, blank=True, null=True)

    def __str__(self):
        return self.name

class EnrollmentRequest(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.course}"
    
