from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet,approve_enrollment,request_enrollment
from . import views


router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('course/<int:course_id>/enroll/', views.request_enrollment, name='request_enrollment'),
    path('enrollment/approve/<int:enrollment_request_id>/', approve_enrollment, name='approve_enrollment'),
]

