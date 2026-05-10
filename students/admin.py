from django.contrib import admin
from students.models import StudentProfile
from teachers.models import TeacherProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'department', 'semester', 'batch', 'cgpa']
    list_filter = ['department', 'semester', 'batch']
    search_fields = ['student_id', 'user__email', 'user__first_name', 'user__last_name']


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'department', 'designation', 'specialization']
    list_filter = ['department', 'designation']
    search_fields = ['employee_id', 'user__email', 'user__first_name', 'user__last_name']
