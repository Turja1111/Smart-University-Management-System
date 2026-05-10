from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        LATE = 'late', 'Late'
        EXCUSED = 'excused', 'Excused'

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'},
        related_name='attendance_records'
    )
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ABSENT)
    marked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='marked_attendance'
    )
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'course', 'date']
        ordering = ['-date']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.student.get_full_name()} | {self.course.code} | {self.date} | {self.status}"
