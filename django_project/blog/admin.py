from django.contrib import admin
from .models import *

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'course', 'due_date')
    search_fields = ('title', 'description', 'course__name')
    list_filter = ('course', 'due_date')
    ordering = ('due_date',)
    date_hierarchy = 'due_date'
    
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('student', 'assignment', 'course', 'submitted_at', 'file')

    # Make fields clickable (links)
    list_display_links = ('student', 'assignment')

    # Define which fields can be searched
    search_fields = ('student__username', 'student__email', 'assignment__title', 'assignment__course__name')

    # Add filters on the right side of the list page
    list_filter = ('assignment__course', 'student', 'assignment')

    # Display a custom title for the form
    fieldsets = (
        ('Submission Details', {
            'fields': ('student', 'assignment', 'file')
        }),
        ('Timestamps', {
            'fields': ('submitted_at',)
        }),
    )

    # Specify read-only fields
    readonly_fields = ('submitted_at',)

    # Prevent admins from selecting students who are not enrolled in the course of the assignment
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            assignment_id = request.resolver_match.kwargs.get('object_id')
            if assignment_id:
                submission = AssignmentSubmission.objects.get(id=assignment_id)
                kwargs["queryset"] = submission.assignment.course.students.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # This allows showing the course in list display
    def course(self, obj):
        return obj.assignment.course.name
    course.short_description = 'Course'

    # Ensure that only students enrolled in the assignment's course are displayed in the dropdown
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['student'].queryset = obj.assignment.course.students.all()
        return form

admin.site.register(AssignmentSubmission, AssignmentSubmissionAdmin)



@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    search_fields = ('title', 'message', 'course__name')
    list_filter = ('course',)
    ordering = ('-title',)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'time_limit')
    search_fields = ('title', 'description', 'course__name')
    list_filter = ('course', 'due_date')
    ordering = ('due_date',)
    date_hierarchy = 'due_date'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'text', 'question_type')
    search_fields = ('text', 'quiz__title')
    list_filter = ('quiz', 'question_type')
    ordering = ('quiz',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'student', 'submitted_at', 'score')
    search_fields = ('quiz__title', 'student__username')
    list_filter = ('quiz', 'student')
    ordering = ('-submitted_at',)
    
    
class DiscussionReplyInline(admin.TabularInline):
    model = DiscussionReply
    extra = 1
    readonly_fields = ('created_by', 'created_at')
    fields = ('content', 'created_by', 'created_at')

    def has_add_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj and obj.created_by == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj and obj.created_by == request.user

@admin.register(DiscussionThread)
class DiscussionThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'created_by', 'created_at')
    list_filter = ('course', 'created_by', 'created_at')
    search_fields = ('title', 'course__name', 'created_by__username')
    readonly_fields = ('created_by', 'created_at')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(DiscussionPost)
class DiscussionPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'created_by', 'created_at', 'content_excerpt')
    list_filter = ('created_at', 'created_by', 'thread')
    search_fields = ('content', 'created_by__username', 'thread__title')
    readonly_fields = ('created_by', 'created_at')
    inlines = [DiscussionReplyInline]

    @admin.display(description='Content')
    def content_excerpt(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    
    
@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'created_by', 'created_at', 'content_excerpt')
    list_filter = ('created_at', 'created_by')
    search_fields = ('content', 'created_by__username', 'post__thread__title')
    readonly_fields = ('created_by', 'created_at')

    @admin.display(description='Content')
    def content_excerpt(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class DiscussionReplyInline(admin.TabularInline):
    model = DiscussionReply
    extra = 1
    readonly_fields = ('created_by', 'created_at')
    fields = ('content', 'created_by', 'created_at')

    def has_add_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj and obj.created_by == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj and obj.created_by == request.user


admin.site.site_header = "Edu Connect Administration"
admin.site.site_title = "Edu Connect Admin Portal"
admin.site.index_title = "Welcome to the Edu Connect Admin Area"
