from django.contrib import admin
from .models import Profile, Follow, Connection, FriendRequest

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'interests', 'skills')
    search_fields = ('user__username', 'bio', 'interests', 'skills')
    list_filter = ('user__role',)

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed', 'created_at')
    search_fields = ('follower__username', 'followed__username')
    list_filter = ('follower__role', 'followed__role')

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2')
    search_fields = ('user1__username', 'user2__username')
    list_filter = ('user1__role', 'user2__role')
    
@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('id','from_user', 'to_user', 'created_at', 'accepted')
    list_filter = ('accepted', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')
    readonly_fields = ('created_at',)