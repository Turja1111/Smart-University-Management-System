"""Exams views"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Max, Min, Count
from rest_framework import serializers as drf_serializers
from django_filters.rest_framework import DjangoFilterBackend

from .models import ExamResult
from accounts.permissions import IsAdminOrTeacher
from courses.models import Course


class ExamResultSerializer(drf_serializers.ModelSerializer):
    student_name = drf_serializers.SerializerMethodField()
    course_code = drf_serializers.SerializerMethodField()
    percentage = drf_serializers.SerializerMethodField()

    class Meta:
        model = ExamResult
        fields = ['id', 'student', 'student_name', 'course', 'course_code',
                  'exam_type', 'marks_obtained', 'total_marks', 'percentage',
                  'grade', 'grade_points', 'semester', 'year', 'remarks',
                  'graded_by', 'created_at']
        read_only_fields = ['grade', 'grade_points', 'created_at']

    def get_student_name(self, obj):
        return obj.student.get_full_name()

    def get_course_code(self, obj):
        return obj.course.code

    def get_percentage(self, obj):
        if obj.total_marks:
            return round((obj.marks_obtained / obj.total_marks) * 100, 1)
        return None


class ExamResultViewSet(viewsets.ModelViewSet):
    serializer_class = ExamResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'exam_type', 'student', 'semester', 'year']

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return ExamResult.objects.all().select_related('student', 'course', 'graded_by')
        if user.is_teacher:
            return ExamResult.objects.filter(
                course__teacher=user
            ).select_related('student', 'course')
        return ExamResult.objects.filter(student=user).select_related('course')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(graded_by=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_results(request):
    """Student: all personal exam results"""
    results = ExamResult.objects.filter(student=request.user).select_related('course')
    data = [{
        'course': r.course.code,
        'exam_type': r.exam_type,
        'marks': f"{r.marks_obtained}/{r.total_marks}",
        'grade': r.grade,
        'grade_points': r.grade_points,
        'semester': r.semester,
        'year': r.year,
    } for r in results]
    return Response({'results': data, 'total': len(data)})


@api_view(['GET'])
@permission_classes([IsAdminOrTeacher])
def course_results(request, course_id):
    """Teacher/Admin: all results for a course"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.is_teacher and course.teacher != request.user:
        return Response({'error': 'Not your course.'}, status=status.HTTP_403_FORBIDDEN)

    results = ExamResult.objects.filter(course=course).select_related('student')
    data = ExamResultSerializer(results, many=True).data
    stats = results.aggregate(avg=Avg('marks_obtained'), high=Max('marks_obtained'), low=Min('marks_obtained'))
    return Response({'course': course.code, 'statistics': stats, 'results': data})
