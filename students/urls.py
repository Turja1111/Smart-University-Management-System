from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.StudentProfileView.as_view(), name='student_profile'),
    path('list/', views.StudentListView.as_view(), name='student_list'),
    path('list/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('cgpa/', views.cgpa_analytics, name='cgpa_analytics'),
    path('routine/', views.my_routine, name='my_routine'),
]
