from rest_framework import serializers
from .models import Course

from users.models import CustomUser

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'teachers', 'students', 'resources']
        
