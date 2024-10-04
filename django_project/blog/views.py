from rest_framework import viewsets, permissions
from django.core.mail import send_mail
from .models import Assignment,AssignmentSubmission, Announcement, Quiz, Question, Submission, DiscussionThread, DiscussionPost, DiscussionReply
from .serializers import AssignmentSerializer,AssignmentSubmissionSerializer, AnnouncementSerializer, QuizSerializer, QuestionSerializer,StudentQuestionSerializer, SubmissionSerializer, DiscussionThreadSerializer, DiscussionPostSerializer, DiscussionReplySerializer
from users.models import CustomUser
from courses.models import Course
from users.serializers import UserSerializer
from courses.serializers import CourseSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import AssignmentPermission, AnnouncementPermission, QuizPermission, QuestionPermission, SubmissionPermission, DiscussionPermissions, AssignmentSubmissionPermission
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AssignmentPermission]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['due_date']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Assignment.objects.all()
        if user.role == 'teacher':
            return Assignment.objects.filter(course__in=user.courses_taught.all())
        if user.role == 'student':
            return Assignment.objects.filter(course__in=user.enrolled_courses.all())

        return Assignment.objects.none()
    
class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AssignmentSubmissionPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return AssignmentSubmission.objects.all()
        if user.role == 'teacher':
            return AssignmentSubmission.objects.filter(assignment__course__in=user.courses_taught.all())
        if user.role == 'student':
            return AssignmentSubmission.objects.filter(student=user)
        
        return AssignmentSubmission.objects.none()

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AnnouncementPermission]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'message']
    ordering_fields = ['course']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Announcement.objects.all()
        if user.role == 'teacher':
            return Announcement.objects.filter(course__in=user.courses_taught.all())
        if user.role == 'student':
            return Announcement.objects.filter(course__in=user.enrolled_courses.all())
        return Announcement.objects.none()

    def perform_create(self, serializer):
        announcement = serializer.save()
        students = announcement.course.students.all()
        for student in students:
            try:
                send_mail(
                    subject=f"New Announcement in {announcement.course.name}",
                    message=announcement.message,
                    from_email='no-reply@example.com',
                    recipient_list=[student.email],
                )
            except Exception as e:
                print(f"Failed to send email to {student.email}: {str(e)}")
        if not students.exists():
            print("No students are enrolled in the course.")


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, QuizPermission]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['due_date']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Quiz.objects.all()
        if user.role == 'teacher':
            return Quiz.objects.filter(course__in=user.courses_taught.all())
        if user.role == 'student':
            return Quiz.objects.filter(course__in=user.enrolled_courses.all())
        return Quiz.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'admin':
            serializer.save()
        elif user.role == 'teacher':
            course = serializer.validated_data.get('course')
            if course in user.courses_taught.all():
                serializer.save()
            else:
                raise PermissionDenied("You can only create quizzes for the courses you teach.")



class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['text']
    ordering_fields = ['quiz']

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_pk')
        user = self.request.user
        if user.role == 'admin':
            return self.queryset.filter(quiz_id=quiz_id)
        if user.role == 'teacher':
            quiz = Quiz.objects.get(id=quiz_id)
            if quiz.course in user.courses_taught.all():
                return self.queryset.filter(quiz_id=quiz_id)
        if user.role == 'student':
            quiz = Quiz.objects.get(id=quiz_id)
            if quiz.course in user.enrolled_courses.all():
                return self.queryset.filter(quiz_id=quiz_id)
        return Question.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        quiz_id = self.kwargs.get('quiz_pk')
        quiz = Quiz.objects.get(id=quiz_id)
        if user.role == 'admin':
            serializer.save()
        elif user.role == 'teacher' and quiz.course in user.courses_taught.all():
            serializer.save()
        else:
            raise PermissionDenied("You can only create questions for quizzes you are assigned to.")

    def perform_update(self, serializer):
        user = self.request.user
        quiz_id = self.kwargs.get('quiz_pk')
        quiz = Quiz.objects.get(id=quiz_id)

        if user.role == 'admin':
            serializer.save()
        elif user.role == 'teacher' and quiz.course in user.courses_taught.all():
            serializer.save()
        else:
            raise PermissionDenied("You can only update questions for quizzes you are assigned to.")

    def get_serializer_class(self):
        user = self.request.user
        if user.role == 'student':
            return StudentQuestionSerializer
        return QuestionSerializer  


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, SubmissionPermission]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__username', 'quiz__title']
    ordering_fields = ['submitted_at']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'teacher']:
            return Submission.objects.all()
        if user.role == 'student':
            return Submission.objects.filter(student=user)
        return Submission.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        quiz = serializer.validated_data.get('quiz')
        if user.role == 'student':
            if Submission.objects.filter(student=user, quiz=quiz).exists():
                raise PermissionDenied("You have already submitted this quiz.")

        submission = serializer.save(student=user)  
        submission.calculate_score()

    def update(self, request, *args, **kwargs):
        if request.user.role == 'student':
            raise PermissionDenied("You cannot update your submission.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role == 'student':
            raise PermissionDenied("You cannot delete your submission.")
        return super().destroy(request, *args, **kwargs)

    
    
class DiscussionThreadViewSet(viewsets.ModelViewSet):
    queryset = DiscussionThread.objects.all()
    serializer_class = DiscussionThreadSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DiscussionPermissions]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return DiscussionThread.objects.all()
        if user.role in ['teacher', 'student']:
            return DiscussionThread.objects.filter(course__in=user.courses_taught.all() if user.role == 'teacher' else user.enrolled_courses.all())  
        return DiscussionThread.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DiscussionPostViewSet(viewsets.ModelViewSet):
    queryset = DiscussionPost.objects.all()
    serializer_class = DiscussionPostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DiscussionPermissions]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return DiscussionPost.objects.all()
        if user.role in ['teacher', 'student']:
            return DiscussionPost.objects.filter(thread__course__in=user.courses_taught.all() if user.role == 'teacher' else user.enrolled_courses.all())       
        return DiscussionPost.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DiscussionReplyViewSet(viewsets.ModelViewSet):
    queryset = DiscussionReply.objects.all()
    serializer_class = DiscussionReplySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DiscussionPermissions]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content']
    ordering_fields = ['created_at']


    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return DiscussionReply.objects.all()
        if user.role in ['teacher', 'student']:
            return DiscussionReply.objects.filter(post__thread__course__in=user.courses_taught.all() if user.role == 'teacher' else user.enrolled_courses.all())
        return DiscussionReply.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)