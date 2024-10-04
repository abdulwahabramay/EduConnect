from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EnrollmentRequest

@receiver(post_save, sender=EnrollmentRequest)
def add_student_to_course(sender, instance, **kwargs):
    if instance.status == 'approved':
        course = instance.course
        course.students.add(instance.student)
