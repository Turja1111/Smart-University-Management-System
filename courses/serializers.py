from rest_framework import serializers
from .models import Department, Course, Enrollment, Assignment, AssignmentSubmission
from django.contrib.auth import get_user_model

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    head_teacher_name = serializers.SerializerMethodField()
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'head_teacher', 'head_teacher_name',
                  'established_year', 'is_active', 'course_count', 'created_at']

    def get_head_teacher_name(self, obj):
        return obj.head_teacher.get_full_name() if obj.head_teacher else None

    def get_course_count(self, obj):
        return obj.courses.filter(is_active=True).count()


class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    enrolled_count = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'description', 'department', 'department_name',
                  'teacher', 'teacher_name', 'credits', 'semester', 'year', 'schedule',
                  'max_students', 'enrolled_count', 'is_full', 'is_active', 'created_at']

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() if obj.teacher else None


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()
    course_code = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_name', 'course', 'course_name', 'course_code',
                  'status', 'enrolled_at', 'dropped_at', 'grade', 'grade_points']
        read_only_fields = ['enrolled_at', 'dropped_at', 'grade', 'grade_points']

    def get_student_name(self, obj):
        return obj.student.get_full_name()

    def get_course_name(self, obj):
        return obj.course.name

    def get_course_code(self, obj):
        return obj.course.code


class AssignmentSerializer(serializers.ModelSerializer):
    course_code = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    submissions_count = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ['id', 'course', 'course_code', 'title', 'description', 'due_date',
                  'total_marks', 'created_by', 'created_by_name', 'is_active', 'submissions_count', 'created_at']
        read_only_fields = ['created_by', 'created_at']

    def get_course_code(self, obj):
        return obj.course.code

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None

    def get_submissions_count(self, obj):
        return obj.submissions.count()


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    assignment_title = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'assignment_title', 'student', 'student_name',
                  'file', 'text_content', 'submitted_at', 'marks_obtained', 'feedback',
                  'ai_summary', 'plagiarism_score', 'is_late', 'graded_at']
        read_only_fields = ['submitted_at', 'is_late', 'graded_at', 'ai_summary', 'plagiarism_score']

    def get_student_name(self, obj):
        return obj.student.get_full_name()

    def get_assignment_title(self, obj):
        return obj.assignment.title
