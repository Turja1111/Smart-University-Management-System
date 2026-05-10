"""Teachers views - Profile, grading, analytics"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count, Max, Min

from .models import TeacherProfile
from .serializers import TeacherProfileSerializer
from accounts.permissions import IsAdmin, IsTeacher, IsAdminOrTeacher
from courses.models import Course, Enrollment, Assignment, AssignmentSubmission
from exams.models import ExamResult


class TeacherProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeacherProfileSerializer

    def get_object(self):
        user = self.request.user
        profile, _ = TeacherProfile.objects.get_or_create(
            user=user,
            defaults={'employee_id': f'TCH{user.id:06d}'}
        )
        return profile


class TeacherListView(generics.ListAPIView):
    """Admin: list all teachers"""
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAdmin]
    queryset = TeacherProfile.objects.select_related('user', 'department').all()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_courses(request):
    """Teacher: list their courses"""
    user = request.user
    if not (user.is_teacher or user.is_admin):
        return Response({'error': 'Teacher access required.'}, status=status.HTTP_403_FORBIDDEN)
    from courses.serializers import CourseSerializer
    courses = Course.objects.filter(teacher=user, is_active=True).select_related('department')
    return Response({'courses': CourseSerializer(courses, many=True).data})


@api_view(['GET'])
@permission_classes([IsAdminOrTeacher])
def exam_analytics(request, course_id):
    """Teacher: exam performance analytics for a course"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
    if request.user.is_teacher and course.teacher != request.user:
        return Response({'error': 'Not your course.'}, status=status.HTTP_403_FORBIDDEN)

    results = ExamResult.objects.filter(course=course)
    stats = results.aggregate(
        avg_marks=Avg('marks_obtained'),
        max_marks=Max('marks_obtained'),
        min_marks=Min('marks_obtained'),
        total_students=Count('student', distinct=True),
    )
    grade_breakdown = {}
    for r in results:
        grade_breakdown[r.grade] = grade_breakdown.get(r.grade, 0) + 1

    return Response({
        'course': course.code,
        'statistics': stats,
        'grade_distribution': grade_breakdown,
        'total_exams': results.count(),
    })
