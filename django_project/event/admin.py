from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'course', 'created_by')  
    list_filter = ('course', 'date') 
    search_fields = ('title', 'description', 'created_by__email') 
    filter_horizontal = ('students',) 

    def get_queryset(self, request):
        """Limit the events a teacher can view to only their own courses."""
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(course__teachers=request.user)

