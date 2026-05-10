"""Courses views - Departments, Courses, Enrollments, Assignments"""
import django.utils.timezone as tz
from django.db import IntegrityError
from rest_framework import generics, viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Department, Course, Enrollment, Assignment, AssignmentSubmission
from .schedule_utils import intervals_overlap, iter_conflict_intervals
from .serializers import (
    DepartmentSerializer, CourseSerializer, EnrollmentSerializer,
    AssignmentSerializer, AssignmentSubmissionSerializer
)
from accounts.permissions import IsAdmin, IsAdminOrTeacher, IsTeacher, IsStudent


class CoursePagination(PageNumberPagination):
    """Courses list can be large after routine import; allow clients to request more per page."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 2000


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['name', 'code']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('department', 'teacher').filter(is_active=True)
    serializer_class = CourseSerializer
    pagination_class = CoursePagination
    filterset_fields = ['department', 'semester', 'year', 'teacher']
    search_fields = ['name', 'code', 'description']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def check_conflicts(self, request):
        """Detect schedule conflicts for a user's enrolled courses"""
        user = request.user
        enrollments = Enrollment.objects.filter(
            student=user, status='enrolled'
        ).select_related('course')
        intervals_by_course: list[tuple[str, str, int, int]] = []
        for e in enrollments:
            c = e.course
            for wd, sm, em, code in iter_conflict_intervals(c.code, c.schedule):
                intervals_by_course.append((code, wd, sm, em))

        conflicts = []
        seen_pairs: set[tuple[tuple[str, str], str]] = set()
        for i, a in enumerate(intervals_by_course):
            code_a, wd_a, sm_a, em_a = a
            for b in intervals_by_course[i + 1 :]:
                code_b, wd_b, sm_b, em_b = b
                if code_a == code_b:
                    continue
                if wd_a != wd_b:
                    continue
                if not intervals_overlap((sm_a, em_a), (sm_b, em_b)):
                    continue
                pair = tuple(sorted((code_a, code_b)))
                key = (pair, wd_a)
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                conflicts.append({
                    'course1': code_a,
                    'course2': code_b,
                    'conflict': f'Both on {wd_a} with overlapping times ({code_a} vs {code_b})',
                })
        return Response({'conflicts': conflicts, 'total': len(conflicts)})


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    filterset_fields = ['status', 'course']

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Enrollment.objects.all().select_related('student', 'course')
        if user.is_teacher:
            return Enrollment.objects.filter(course__teacher=user).select_related('student', 'course')
        return Enrollment.objects.filter(student=user).select_related('course')

    def get_permissions(self):
        if self.action in ['create']:
            return [IsStudent()]
        if self.action in ['update', 'partial_update']:
            return [IsAdminOrTeacher()]
        if self.action == 'destroy':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        try:
            course = Course.objects.get(id=course_id, is_active=True)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        if course.is_full:
            return Response({'error': 'Course is full.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            enrollment = Enrollment.objects.create(student=request.user, course=course)
            return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'error': 'Already enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        enrollment = self.get_object()
        if not request.user.is_admin and enrollment.student != request.user:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        enrollment.status = 'dropped'
        enrollment.dropped_at = tz.now()
        enrollment.save()
        return Response({'message': 'Course dropped successfully.'})


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    filterset_fields = ['course', 'is_active']

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Assignment.objects.all().select_related('course', 'created_by')
        if user.is_teacher:
            return Assignment.objects.filter(course__teacher=user).select_related('course')
        # Students see assignments for their enrolled active courses
        enrolled_courses = Enrollment.objects.filter(
            student=user, status='enrolled'
        ).values_list('course_id', flat=True)
        return Assignment.objects.filter(course__in=enrolled_courses, is_active=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return AssignmentSubmission.objects.all().select_related('student', 'assignment')
        if user.is_teacher:
            return AssignmentSubmission.objects.filter(
                assignment__course__teacher=user
            ).select_related('student', 'assignment')
        return AssignmentSubmission.objects.filter(student=user)

    def get_permissions(self):
        if self.action == 'create':
            return [IsStudent()]
        if self.action in ['update', 'partial_update']:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrTeacher])
    def grade(self, request, pk=None):
        submission = self.get_object()
        marks = request.data.get('marks_obtained')
        feedback = request.data.get('feedback', '')
        if marks is None:
            return Response({'error': 'marks_obtained required.'}, status=status.HTTP_400_BAD_REQUEST)
        submission.marks_obtained = marks
        submission.feedback = feedback
        submission.graded_at = tz.now()
        submission.graded_by = request.user
        submission.save()
        return Response(AssignmentSubmissionSerializer(submission).data)
