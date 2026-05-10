from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('results', views.ExamResultViewSet, basename='exam_results')

urlpatterns = [
    path('', include(router.urls)),
    path('my-results/', views.my_results, name='my_results'),
    path('course-results/<int:course_id>/', views.course_results, name='course_results'),
]
