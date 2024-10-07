from rest_framework import permissions
from courses.models import Course
from rest_framework.exceptions import PermissionDenied

class AssignmentPermission(permissions.BasePermission):
    """
    Custom permission to allow:
    - Admin: full access (create, view, edit, delete).
    - Teacher: can create and view assignments for their assigned courses.
    - Student: can only view assignments if they are enrolled in the course.
    """

    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return request.user.role in ['admin', 'teacher']
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        
        if request.user.role == 'teacher':
            return obj.course in request.user.courses_taught.all()

        if request.user.role == 'student' and view.action == 'retrieve':
            return obj.course in request.user.enrolled_courses.all()

        return False
    
class AssignmentSubmissionPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow GET requests for all authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Allow POST and PUT requests for students submitting their own work
        if request.user.role == 'student':
            return obj.student == request.user
        
        # Allow teachers and admins to view and manage submissions
        if request.user.role == 'teacher':
            return obj.assignment.course in request.user.courses_taught.all()
        
        return request.user.role == 'admin'

class AnnouncementPermission(permissions.BasePermission):
    """
    Custom permission to allow:
    - Admin: full access (create, view, update, delete).
    - Teacher: can create and view announcements for their assigned courses.
    - Student: can only view announcements if they are enrolled in the course.
    """

    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return request.user.role in ['admin', 'teacher']
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'teacher':
            return obj.course in request.user.courses_taught.all()
        if request.user.role == 'student' and view.action == 'retrieve':
            return obj.course in request.user.enrolled_courses.all()
        return False
    
class QuizPermission(permissions.BasePermission):
    """
    Custom permission to allow only admins and teachers to create, update, and delete quizzes.
    Students can only view quizzes.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'teacher']:
            return True
        if request.user.role == 'student' and view.action in ['retrieve', 'list']:
            return True
        return False



class QuestionPermission(permissions.BasePermission):
    """
    Custom permission to allow only admins and teachers to create and modify questions.
    Students can only view questions.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'teacher']:
            return True
        if request.user.role == 'student' and view.action in ['retrieve', 'list']:
            return True
        return False


class SubmissionPermission(permissions.BasePermission):
    """
    Custom permission to allow:
    - Admins and teachers: Full access (view, create, update, delete)
    - Students: Can only submit (POST) once for a specific quiz, and view (GET) their own submissions.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role in ['admin', 'teacher']:
            return True
        if request.user.role == 'student':
            if view.action in ['create', 'retrieve', 'list']:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'teacher']:
            return True
        if request.user.role == 'student':
            if view.action in ['retrieve', 'list']:
                return obj.student == request.user
            return False
        return False



class DiscussionPermissions(permissions.BasePermission):
    """
    Custom permission that allows:
    - Admins: full access (create, update, delete, view).
    - Teachers/Students: can create and view threads/posts only in assigned courses.
    - Teachers/Students: can update or delete only their own threads/posts.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.role == 'admin':
            return True
        if user.role in ['teacher', 'student']:
            if request.method in ['GET', 'POST', 'HEAD', 'OPTIONS']:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'admin':
            return True
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.created_by == user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return False