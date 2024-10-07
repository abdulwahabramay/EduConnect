from django.db import models
from django.conf import settings
from courses.models import Course

class Resource(models.Model):
    file = models.FileField(upload_to='resources/media')
    category = models.CharField(max_length=100)
    tags = models.CharField(max_length=255)
    courses = models.ForeignKey(Course, related_name='resources', on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resources')


    def __str__(self):
        return self.file.name