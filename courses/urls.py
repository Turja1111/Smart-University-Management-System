from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('departments', views.DepartmentViewSet, basename='departments')
router.register('courses', views.CourseViewSet, basename='courses')
router.register('enrollments', views.EnrollmentViewSet, basename='enrollments')
router.register('assignments', views.AssignmentViewSet, basename='assignments')
router.register('submissions', views.AssignmentSubmissionViewSet, basename='submissions')

urlpatterns = [
    path('', include(router.urls)),
]
