from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('records', views.AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
    path('bulk-mark/', views.bulk_mark_attendance, name='bulk_mark_attendance'),
    path('my-attendance/', views.my_attendance, name='my_attendance'),
    path('analytics/<int:course_id>/', views.attendance_analytics, name='attendance_analytics'),
]
