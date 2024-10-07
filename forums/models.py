from django.db import models
from django.conf import settings  
from courses.models import Course

class Forum(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    course = models.ForeignKey(Course, related_name='forums', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='forums', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Comment(models.Model):
    forum = models.ForeignKey(Forum, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.created_by} on {self.forum.title}"
