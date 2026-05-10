from django.contrib import admin
from .models import ExamResult


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'exam_type', 'marks_obtained', 'total_marks', 'grade', 'grade_points', 'created_at']
    list_filter = ['exam_type', 'grade', 'semester', 'year']
    search_fields = ['student__email', 'course__code']
