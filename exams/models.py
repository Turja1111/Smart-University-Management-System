from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ExamResult(models.Model):
    class ExamType(models.TextChoices):
        QUIZ = 'quiz', 'Quiz'
        MIDTERM = 'midterm', 'Midterm'
        FINAL = 'final', 'Final'
        ASSIGNMENT = 'assignment', 'Assignment'
        LAB = 'lab', 'Lab'

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'},
        related_name='exam_results'
    )
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='exam_results')
    exam_type = models.CharField(max_length=15, choices=ExamType.choices)
    marks_obtained = models.FloatField()
    total_marks = models.FloatField(default=100.0)
    grade = models.CharField(max_length=5, blank=True)
    grade_points = models.FloatField(null=True, blank=True)
    semester = models.CharField(max_length=10, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='graded_results'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Exam Result'
        verbose_name_plural = 'Exam Results'

    def __str__(self):
        return f"{self.student.get_full_name()} | {self.course.code} | {self.exam_type} | {self.marks_obtained}/{self.total_marks}"

    def save(self, *args, **kwargs):
        # Auto-calculate grade
        if self.marks_obtained is not None and self.total_marks:
            percentage = (self.marks_obtained / self.total_marks) * 100
            self.grade, self.grade_points = self._calculate_grade(percentage)
        super().save(*args, **kwargs)

    @staticmethod
    def _calculate_grade(percentage):
        if percentage >= 90: return 'A+', 4.0
        elif percentage >= 85: return 'A', 4.0
        elif percentage >= 80: return 'A-', 3.7
        elif percentage >= 75: return 'B+', 3.3
        elif percentage >= 70: return 'B', 3.0
        elif percentage >= 65: return 'B-', 2.7
        elif percentage >= 60: return 'C+', 2.3
        elif percentage >= 55: return 'C', 2.0
        elif percentage >= 50: return 'D', 1.0
        else: return 'F', 0.0
