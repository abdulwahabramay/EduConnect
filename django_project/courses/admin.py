from django.contrib import admin
from .models import Course, EnrollmentRequest

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