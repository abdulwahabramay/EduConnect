from django.contrib import admin
from .models import Course, EnrollmentRequest, CourseActivityLog

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'description') 
    search_fields = ('name', 'description')
    filter_horizontal = ('teachers', 'students') 

    def get_queryset(self, request):
        """Filter courses by teacher if the user is not a superuser."""
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(teachers=request.user)


admin.site.register(EnrollmentRequest)

@admin.register(CourseActivityLog)
class CourseActivityLogAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'action', 'timestamp')  # Columns to display in the list view
    list_filter = ('action', 'timestamp')  # Filter options in the right sidebar
    search_fields = ('course__name', 'user__username')  # Fields to search in the admin interface
    ordering = ('-timestamp',)  # Order by timestamp descending

    # Optional: Add custom actions if needed
    actions = ['mark_as_created', 'mark_as_updated', 'mark_as_deleted']

    def mark_as_created(self, request, queryset):
        # Custom action to mark selected logs as created
        queryset.update(action='create')
        self.message_user(request, "Selected logs marked as created.")

    def mark_as_updated(self, request, queryset):
        # Custom action to mark selected logs as updated
        queryset.update(action='update')
        self.message_user(request, "Selected logs marked as updated.")

    def mark_as_deleted(self, request, queryset):
        # Custom action to mark selected logs as deleted
        queryset.update(action='delete')
        self.message_user(request, "Selected logs marked as deleted.")

    mark_as_created.short_description = "Mark selected logs as created"
    mark_as_updated.short_description = "Mark selected logs as updated"
    mark_as_deleted.short_description = "Mark selected logs as deleted"