from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, CourseActivityLog
from users.models import CustomUser  

@receiver(post_save, sender=Course)
def send_course_creation_email(sender, instance, created, **kwargs):
    if created:
        users = CustomUser.objects.all() 
        subject = f"New Course Created: {instance.name}"
        message = f"A new course has been created:\n\nName: {instance.name}\nDescription: {instance.description}\n\nCheck it out on the platform!"
        from_email = settings.EMAIL_HOST_USER

        recipient_list = [user.email for user in users if user.email]
        send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=Course)
def log_course_save(sender, instance, created, **kwargs):
    if created:
        action = 'create'
    else:
        action = 'update'

    if instance.created_by:
        CourseActivityLog.objects.create(
            course=instance,
            user=instance.created_by,
            action=action
        )
    

@receiver(post_delete, sender=Course)
def log_course_delete(sender, instance, **kwargs):
    # Log the delete action (no user is tied to this in the signal directly, so may need to pass through the view)
    if instance.created_by:
        CourseActivityLog.objects.create(
            course=instance,
            user=instance.created_by,
            action='delete'
        )