from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        'courses.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='teachers'
    )
    specialization = models.CharField(max_length=200, blank=True)
    qualification = models.CharField(max_length=200, blank=True, help_text='e.g. PhD in CS')
    designation = models.CharField(max_length=100, blank=True, help_text='e.g. Assistant Professor')
    bio = models.TextField(blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    office_room = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
