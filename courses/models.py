from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    head_teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role': 'teacher'}, related_name='headed_departments'
    )
    established_year = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    class Semester(models.TextChoices):
        SPRING = 'spring', 'Spring'
        SUMMER = 'summer', 'Summer'
        FALL = 'fall', 'Fall'

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role': 'teacher'}, related_name='teaching_courses'
    )
    credits = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(6)])
    semester = models.CharField(max_length=10, choices=Semester.choices, default=Semester.FALL)
    year = models.PositiveIntegerField(default=2026)
    schedule = models.JSONField(default=dict, blank=True, help_text='{"days": ["Mon","Wed"], "time": "10:00-11:30", "room": "101"}')
    max_students = models.PositiveIntegerField(default=40)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def enrolled_count(self):
        return self.enrollments.filter(status='enrolled').count()

    @property
    def is_full(self):
        return self.enrolled_count >= self.max_students


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ENROLLED = 'enrolled', 'Enrolled'
        DROPPED = 'dropped', 'Dropped'
        COMPLETED = 'completed', 'Completed'
        WITHDRAWN = 'withdrawn', 'Withdrawn'

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'},
        related_name='enrollments'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ENROLLED)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    dropped_at = models.DateTimeField(null=True, blank=True)
    grade = models.CharField(max_length=5, blank=True, help_text='Final grade e.g. A, B+')
    grade_points = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.course.code}"


class AdvisingConfirmation(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='advising_confirmations'
    )
    semester = models.CharField(max_length=10, choices=Course.Semester.choices)
    year = models.PositiveIntegerField()

    student_confirmed = models.BooleanField(default=False)
    student_confirmed_at = models.DateTimeField(null=True, blank=True)

    teacher_approved = models.BooleanField(default=False)
    teacher_approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_advisings',
        limit_choices_to={'role': 'teacher'}
    )

    courses_snapshot = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'semester', 'year']
        ordering = ['-created_at']

    def __str__(self):
        return f"Advising {self.student.get_full_name()} {self.semester} {self.year}"


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=300)
    description = models.TextField()
    due_date = models.DateTimeField()
    total_marks = models.PositiveIntegerField(default=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_assignments')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.code} - {self.title}"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'},
        related_name='submissions'
    )
    file = models.FileField(upload_to='submissions/%Y/%m/', null=True, blank=True)
    text_content = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True, help_text='AI-generated summary of submission')
    plagiarism_score = models.FloatField(null=True, blank=True, help_text='Percentage similarity (0-100)')
    is_late = models.BooleanField(default=False)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='graded_submissions')

    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.assignment.title}"

    def save(self, *args, **kwargs):
        if self.assignment_id:
            import django.utils.timezone as tz
            self.is_late = tz.now() > self.assignment.due_date
        super().save(*args, **kwargs)
