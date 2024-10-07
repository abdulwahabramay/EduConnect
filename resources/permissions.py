from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrTeacherOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins and teachers to edit or delete resources.
    Students can only read resources for courses they are enrolled in.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            return request.user.role in ['admin', 'teacher']  
        
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.courses.students.filter(id=request.user.id).exists()
        return obj.uploaded_by == request.user or request.user.role == 'admin' or request.user.role == 'teacher'
