from django.db import models
from courses.models import Course
from users.models import CustomUser

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    students = models.ManyToManyField(CustomUser, related_name='event_students', limit_choices_to={'role': 'student'})

    def __str__(self):
        return self.title