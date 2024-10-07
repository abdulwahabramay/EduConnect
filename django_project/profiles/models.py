from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    interests = models.TextField(blank=True)
    skills = models.TextField(blank=True)

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_friend_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.from_user.username} to {self.to_user.username}"

    class Meta:
        unique_together = ('from_user', 'to_user')

class Connection(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='connections_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='connections_as_user2', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user1.username} connected with {self.user2.username}"

    class Meta:
        unique_together = ('user1', 'user2')