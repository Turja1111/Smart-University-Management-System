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
from .models import AdvisingConfirmation
from .schedule_utils import intervals_overlap, iter_conflict_intervals
from django.db.models import F

from .serializers import (
    DepartmentSerializer, CourseSerializer, EnrollmentSerializer,
    AssignmentSerializer, AssignmentSubmissionSerializer
)
from .serializers import AdvisingConfirmationSerializer
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
        # Prevent changes once student has confirmed advising for this semester/year
        if not request.user.is_admin and getattr(request.user, 'is_student', False):
            try:
                conf = AdvisingConfirmation.objects.get(student=request.user, semester=course.semester, year=course.year)
                if conf.student_confirmed and not conf.teacher_approved:
                    return Response({'error': 'Advising already confirmed by student. Cannot change courses until teacher approval.'}, status=status.HTTP_400_BAD_REQUEST)
            except AdvisingConfirmation.DoesNotExist:
                pass
        if course.is_full:
            return Response({'error': 'Course is full.'}, status=status.HTTP_400_BAD_REQUEST)

        # Enforce maximum 5 courses per semester rule
        active_enrollments_count = Enrollment.objects.filter(
            student=request.user,
            status=Enrollment.Status.ENROLLED,
            course__semester=course.semester,
            course__year=course.year
        ).count()
        if active_enrollments_count >= 5:
            return Response({'error': 'You cannot select more than 5 courses per semester.'}, status=status.HTTP_400_BAD_REQUEST)

        # If an enrollment record already exists for this student+course,
        # reactivate it when appropriate instead of creating a duplicate
        existing = Enrollment.objects.filter(student=request.user, course=course).first()
        if existing:
            if existing.status == Enrollment.Status.ENROLLED:
                return Response({'error': 'Already enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)
            # Reactivate dropped/withdrawn/completed enrollment
            existing.status = Enrollment.Status.ENROLLED
            existing.dropped_at = None
            existing.enrolled_at = tz.now()
            existing.save()
            return Response(EnrollmentSerializer(existing).data, status=status.HTTP_200_OK)

        try:
            enrollment = Enrollment.objects.create(student=request.user, course=course)
            return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            # Fallback: if race condition occurs, return friendly message
            return Response({'error': 'Already enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        enrollment = self.get_object()
        if not request.user.is_admin and enrollment.student != request.user:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        # Prevent dropping if student has confirmed advising for this semester/year
        try:
            course = enrollment.course
            conf = AdvisingConfirmation.objects.get(student=enrollment.student, semester=course.semester, year=course.year)
            if conf.student_confirmed and not conf.teacher_approved and enrollment.student == request.user:
                return Response({'error': 'Advising already confirmed by student. Cannot change courses until teacher approval.'}, status=status.HTTP_400_BAD_REQUEST)
        except AdvisingConfirmation.DoesNotExist:
            pass

        enrollment.status = 'dropped'
        enrollment.dropped_at = tz.now()
        enrollment.save()
        return Response({'message': 'Course dropped successfully.'})


class AdvisingConfirmationViewSet(viewsets.ModelViewSet):
    serializer_class = AdvisingConfirmationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return AdvisingConfirmation.objects.all().select_related('student', 'approved_by')
        if user.is_teacher and user.is_verified:
            return AdvisingConfirmation.objects.all().select_related('student', 'approved_by')
        if user.is_teacher:
            # Unverified teachers should only see confirmations for students who have enrollments
            # in this teacher's courses for the same semester and year.
            return AdvisingConfirmation.objects.filter(
                student__enrollments__course__teacher=user,
                student__enrollments__status=Enrollment.Status.ENROLLED,
                student__enrollments__course__semester=F('semester'),
                student__enrollments__course__year=F('year')
            ).select_related('student', 'approved_by').distinct()
        return AdvisingConfirmation.objects.filter(student=user).select_related('approved_by')

    def get_permissions(self):
        from accounts.permissions import IsAdminOrTeacher, IsVerifiedTeacher, IsTeacher, IsStudent
        if self.action in ['create']:
            return [IsStudent()]
        if self.action in ['approve']:
            return [IsVerifiedTeacher()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        # Student confirming their advising for a semester/year
        semester = request.data.get('semester')
        year = request.data.get('year')
        if not semester or not year:
            return Response({'error': 'semester and year required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Enforce min 3, max 5 courses per semester
        enrollments = Enrollment.objects.filter(student=request.user, status='enrolled', course__semester=semester, course__year=year)
        course_count = enrollments.count()
        if course_count < 3:
            return Response({'error': 'You must select at least 3 courses per semester to confirm advising.'}, status=status.HTTP_400_BAD_REQUEST)
        if course_count > 5:
            return Response({'error': 'You cannot select more than 5 courses per semester.'}, status=status.HTTP_400_BAD_REQUEST)

        obj, created = AdvisingConfirmation.objects.get_or_create(student=request.user, semester=semester, year=year)
        if obj.student_confirmed:
            return Response(AdvisingConfirmationSerializer(obj).data, status=status.HTTP_200_OK)
        obj.student_confirmed = True
        obj.student_confirmed_at = tz.now()
        # Snapshot current enrolled course ids for this student/semester/year so the
        # advising selection remains stable even if the client state changes later.
        enrollments = Enrollment.objects.filter(student=request.user, status='enrolled', course__semester=semester, course__year=year)
        obj.courses_snapshot = list(enrollments.values_list('course_id', flat=True))
        obj.save()

        from notifications.models import Notice
        teacher_ids = set(Course.objects.filter(id__in=obj.courses_snapshot, teacher__isnull=False).values_list('teacher_id', flat=True))
        for t_id in teacher_ids:
            Notice.objects.create(
                title=f"Advising Request from {request.user.get_full_name()}",
                content=f"Student {request.user.get_full_name()} has confirmed their advising for {semester} {year}. Please review it.",
                target_role=Notice.TargetRole.TEACHER,
                target_user_id=t_id,
                created_by=request.user
            )

        return Response(AdvisingConfirmationSerializer(obj).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[])
    def approve(self, request, pk=None):
        # Teacher approves student's advising and snapshot courses
        try:
            obj = self.get_object()
        except Exception:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        if obj.teacher_approved:
            return Response(AdvisingConfirmationSerializer(obj).data)
        # snapshot current enrolled course ids for the student for this semester/year
        enrollments = Enrollment.objects.filter(student=obj.student, status='enrolled', course__semester=obj.semester, course__year=obj.year)
        obj.courses_snapshot = list(enrollments.values_list('course_id', flat=True))
        obj.teacher_approved = True
        obj.teacher_approved_at = tz.now()
        obj.approved_by = request.user
        obj.save()

        from notifications.models import Notice
        Notice.objects.create(
            title=f"Advising Approved for {obj.semester} {obj.year}",
            content=f"Your advising request for {obj.semester} {obj.year} has been approved by {request.user.get_full_name()}.",
            target_role=Notice.TargetRole.STUDENT,
            target_user=obj.student,
            created_by=request.user
        )

        return Response(AdvisingConfirmationSerializer(obj).data)


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
