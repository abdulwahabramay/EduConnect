from django.contrib import admin
from .models import Forum, Comment

@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_by') 
    search_fields = ('title', 'content')  
    list_filter = ('course', 'created_by')  
    ordering = ('title',)  

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('forum', 'created_by', 'content')  
    search_fields = ('content', 'forum__title')  
    list_filter = ('forum', 'created_by') 
    ordering = ('forum',)  
