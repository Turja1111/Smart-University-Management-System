"""Attendance views"""
from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers as drf_serializers

from .models import AttendanceRecord
from accounts.permissions import IsAdminOrTeacher, IsTeacher
from courses.models import Course, Enrollment


class AttendanceSerializer(drf_serializers.ModelSerializer):
    student_name = drf_serializers.SerializerMethodField()
    course_code = drf_serializers.SerializerMethodField()

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'student', 'student_name', 'course', 'course_code',
                  'date', 'status', 'marked_by', 'remarks', 'created_at']
        read_only_fields = ['marked_by', 'created_at']

    def get_student_name(self, obj):
        return obj.student.get_full_name()

    def get_course_code(self, obj):
        return obj.course.code


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'date', 'status', 'student']

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return AttendanceRecord.objects.all().select_related('student', 'course', 'marked_by')
        if user.is_teacher:
            return AttendanceRecord.objects.filter(
                course__teacher=user
            ).select_related('student', 'course')
        return AttendanceRecord.objects.filter(student=user).select_related('course')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)


@api_view(['POST'])
@permission_classes([IsAdminOrTeacher])
def bulk_mark_attendance(request):
    """Mark attendance for multiple students at once"""
    course_id = request.data.get('course')
    date = request.data.get('date')
    records = request.data.get('records', [])  # [{"student": id, "status": "present"}, ...]

    if not course_id or not date or not records:
        return Response({'error': 'course, date, and records are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.is_teacher and course.teacher != request.user:
        return Response({'error': 'Not your course.'}, status=status.HTTP_403_FORBIDDEN)

    created, updated = 0, 0
    for record in records:
        obj, was_created = AttendanceRecord.objects.update_or_create(
            student_id=record['student'],
            course=course,
            date=date,
            defaults={
                'status': record.get('status', 'absent'),
                'marked_by': request.user,
                'remarks': record.get('remarks', '')
            }
        )
        if was_created:
            created += 1
        else:
            updated += 1

    return Response({'message': f'{created} created, {updated} updated.', 'total': len(records)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_attendance(request):
    """Student: view personal attendance"""
    user = request.user
    records = AttendanceRecord.objects.filter(student=user).select_related('course')
    course_stats = {}
    for r in records:
        code = r.course.code
        if code not in course_stats:
            course_stats[code] = {'present': 0, 'absent': 0, 'late': 0, 'excused': 0, 'total': 0}
        course_stats[code][r.status] = course_stats[code].get(r.status, 0) + 1
        course_stats[code]['total'] += 1

    summary = []
    for code, stats in course_stats.items():
        total = stats['total']
        present = stats['present'] + stats['late']
        summary.append({
            'course': code,
            'total_classes': total,
            'present': present,
            'absent': stats['absent'],
            'percentage': round((present / total * 100), 1) if total > 0 else 0,
        })
    return Response({'attendance_summary': summary})


@api_view(['GET'])
@permission_classes([IsAdminOrTeacher])
def attendance_analytics(request, course_id):
    """Teacher: attendance analytics for a course"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)

    records = AttendanceRecord.objects.filter(course=course)
    total_classes = records.values('date').distinct().count()
    student_stats = []
    enrolled = Enrollment.objects.filter(course=course, status='enrolled').select_related('student')

    for e in enrolled:
        s = e.student
        s_records = records.filter(student=s)
        present = s_records.filter(status__in=['present', 'late']).count()
        percentage = round((present / total_classes * 100), 1) if total_classes > 0 else 0
        student_stats.append({
            'student': s.get_full_name(),
            'email': s.email,
            'present': present,
            'absent': s_records.filter(status='absent').count(),
            'percentage': percentage,
            'status': 'at_risk' if percentage < 75 else 'ok'
        })

    return Response({
        'course': course.code,
        'total_classes': total_classes,
        'enrolled_students': len(student_stats),
        'student_stats': sorted(student_stats, key=lambda x: x['percentage']),
    })
