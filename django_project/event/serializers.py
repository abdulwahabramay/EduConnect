from rest_framework import serializers
from .models import Event
from users.models import CustomUser


class EventSerializer(serializers.ModelSerializer):
    select_all_students = serializers.BooleanField(write_only=True, default=False)  
    students = serializers.ListField(child=serializers.IntegerField(), write_only=True, default=[])

    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'course', 'students', 'created_by', 'select_all_students']
        read_only_fields = ['created_by']  

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('select_all_students', None) 
        return data

    def create(self, validated_data):
        select_all_students = validated_data.pop('select_all_students', False)  
        students_data = validated_data.pop('students', [])  
        event = Event.objects.create(**validated_data)
        if select_all_students:
            course = validated_data['course']
            students = course.students.all()
            event.students.set(students)  
        else:
            if not students_data:
                raise serializers.ValidationError({'students': 'This field is required when select_all_students is false.'})
            student_objects = CustomUser.objects.filter(id__in=students_data, role='student')
            if not student_objects.exists():
                raise serializers.ValidationError({'students': 'No valid student IDs provided.'})
            event.students.set(student_objects) 
        return event 