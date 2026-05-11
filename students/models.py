from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        'courses.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='students'
    )
    semester = models.PositiveSmallIntegerField(default=1)
    batch = models.CharField(max_length=10, blank=True, help_text='e.g. 2023')
    cgpa = models.FloatField(default=0.0)
    total_credits_completed = models.PositiveIntegerField(default=0)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact = models.CharField(max_length=40, blank=True, help_text='Phone or alternate contact')
    birth_certificate_no = models.CharField(max_length=80, blank=True)
    passport_no = models.CharField(max_length=40, blank=True)
    admission_session = models.CharField(
        max_length=40, blank=True, help_text='e.g. SPRING 2022'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

    def calculate_cgpa(self):
        """Recalculate CGPA from all enrollments with grade points"""
        from courses.models import Enrollment
        enrollments = Enrollment.objects.filter(
            student=self.user, status='completed', grade_points__isnull=False
        )
        if not enrollments.exists():
            return 0.0
        total_points = sum(e.grade_points * e.course.credits for e in enrollments)
        total_credits = sum(e.course.credits for e in enrollments)
        return round(total_points / total_credits, 2) if total_credits > 0 else 0.0
