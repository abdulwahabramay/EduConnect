from rest_framework import permissions

class CustomUserPermission(permissions.BasePermission):
    """
    Custom permission to allow:
    - Admin: can view all users
    - Teacher: can view their own data and students assigned to them
    - Student: can view only their own data
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True

        if request.user.role == 'teacher':
            return obj == request.user or obj in request.user.teachers.all()

        if request.user.role == 'student':
            return obj == request.user

        return False
