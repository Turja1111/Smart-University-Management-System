from django.urls import path

from . import views


urlpatterns = [
    path("", views.root_redirect, name="root"),
    path("login/", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    # Student
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    path("student/attendance/", views.student_attendance, name="student_attendance"),
    path("student/exams/", views.student_exams, name="student_exams"),
    # Teacher
    path("teacher/dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacher/attendance/", views.teacher_attendance, name="teacher_attendance"),
    path("teacher/grades/", views.teacher_grades, name="teacher_grades"),
    # Admin
    path("admin-panel/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/users/", views.admin_users, name="admin_users"),
    path("admin-panel/departments/", views.admin_departments, name="admin_departments"),
    # Shared
    path("courses/", views.shared_courses, name="shared_courses"),
    path("notices/", views.shared_notices, name="shared_notices"),
    path("ai/", views.shared_ai, name="shared_ai"),
]

