from django.contrib import admin
from .models import Department, Course, Enrollment, Assignment, AssignmentSubmission


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head_teacher', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'teacher', 'credits', 'semester', 'year', 'enrolled_count', 'is_active']
    list_filter = ['semester', 'year', 'is_active', 'department']
    search_fields = ['name', 'code']
    autocomplete_fields = ['teacher', 'department']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'grade', 'enrolled_at']
    list_filter = ['status', 'course__semester']
    search_fields = ['student__email', 'course__code']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'due_date', 'total_marks', 'is_active', 'created_at']
    list_filter = ['is_active', 'course']
    search_fields = ['title', 'course__code']


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'submitted_at', 'marks_obtained', 'is_late']
    list_filter = ['is_late']
    search_fields = ['student__email', 'assignment__title']
