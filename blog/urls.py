# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet, AssignmentSubmissionViewSet, AnnouncementViewSet, QuizViewSet, QuestionViewSet, SubmissionViewSet, DiscussionThreadViewSet, DiscussionPostViewSet, DiscussionReplyViewSet

router = DefaultRouter()
router.register(r'assignments', AssignmentViewSet)
router.register(r'announcements', AnnouncementViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'quizzes/(?P<quiz_pk>[^/.]+)/questions', QuestionViewSet, basename='quiz-questions')
router.register(r'questions', QuestionViewSet)
router.register(r'submissions', SubmissionViewSet)
router.register(r'discussion-threads', DiscussionThreadViewSet)
router.register(r'discussion-posts', DiscussionPostViewSet)
router.register(r'discussion-replies', DiscussionReplyViewSet)
router.register(r'assignment-submissions', AssignmentSubmissionViewSet, basename='assignment-submission')

urlpatterns = [
    path('', include(router.urls)),
    
]
