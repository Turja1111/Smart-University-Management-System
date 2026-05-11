"""Students views - Profile, CGPA analytics, routine"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import StudentProfile
from .serializers import StudentProfileSerializer, StudentProfileUpdateSerializer
from accounts.permissions import IsAdmin, IsStudent
from courses.models import Enrollment
from courses.schedule_utils import build_by_day_for_enrollments


class StudentProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return StudentProfileUpdateSerializer
        return StudentProfileSerializer

    def get_object(self):
        user = self.request.user
        profile, _ = StudentProfile.objects.get_or_create(
            user=user,
            defaults={'student_id': f'STU{user.id:06d}'}
        )
        return profile


class StudentListView(generics.ListAPIView):
    """Admin/Teacher: list all students"""
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAdmin]
    queryset = StudentProfile.objects.select_related('user', 'department').all()


class StudentDetailView(generics.RetrieveAPIView):
    """Admin/Teacher: view a student profile"""
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAdmin]
    queryset = StudentProfile.objects.select_related('user', 'department').all()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cgpa_analytics(request):
    """Student CGPA analytics breakdown"""
    user = request.user
    if not user.is_student:
        return Response({'error': 'Student access only.'}, status=status.HTTP_403_FORBIDDEN)

    enrollments = Enrollment.objects.filter(
        student=user, status='completed'
    ).select_related('course')

    total_points = 0.0
    total_credits = 0
    grade_distribution = {'A+': 0, 'A': 0, 'A-': 0, 'B+': 0, 'B': 0, 'B-': 0, 'C+': 0, 'C': 0, 'D': 0, 'F': 0}
    semester_performance = {}

    for e in enrollments:
        if e.grade_points is not None:
            points = e.grade_points * e.course.credits
            total_points += points
            total_credits += e.course.credits
        if e.grade:
            grade_key = e.grade if e.grade in grade_distribution else 'F'
            grade_distribution[grade_key] += 1
        sem_key = f"{e.course.semester.title()} {e.course.year}"
        if sem_key not in semester_performance:
            semester_performance[sem_key] = {'points': 0.0, 'credits': 0}
        if e.grade_points:
            semester_performance[sem_key]['points'] += e.grade_points * e.course.credits
            semester_performance[sem_key]['credits'] += e.course.credits

    cgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    sem_list = []
    for sem, data in semester_performance.items():
        gpa = round(data['points'] / data['credits'], 2) if data['credits'] > 0 else 0.0
        sem_list.append({'semester': sem, 'gpa': gpa, 'credits': data['credits']})

    return Response({
        'cgpa': cgpa,
        'total_credits': total_credits,
        'completed_courses': enrollments.count(),
        'grade_distribution': grade_distribution,
        'semester_performance': sem_list,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_routine(request):
    """Student class schedule/routine"""
    user = request.user
    enrollments = Enrollment.objects.filter(
        student=user, status='enrolled'
    ).select_related('course', 'course__teacher', 'course__department')
    enroll_list = list(enrollments)
    routine = []
    for e in enroll_list:
        c = e.course
        routine.append({
            'course_id': c.id,
            'course_code': c.code,
            'course_name': c.name,
            'teacher': c.teacher.get_full_name() if c.teacher else 'TBA',
            'credits': c.credits,
            'schedule': c.schedule,
            'semester': c.semester,
            'year': c.year,
        })
    by_day = build_by_day_for_enrollments(enroll_list)
    return Response({
        'by_day': by_day,
        'routine': routine,
        'total_courses': len(routine),
    })
