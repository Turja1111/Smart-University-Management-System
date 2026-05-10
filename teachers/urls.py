from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.TeacherProfileView.as_view(), name='teacher_profile'),
    path('list/', views.TeacherListView.as_view(), name='teacher_list'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('exam-analytics/<int:course_id>/', views.exam_analytics, name='exam_analytics'),
]
