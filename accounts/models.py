from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model with role-based access control"""

    class Role(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        TEACHER = 'teacher', _('Teacher')
        STUDENT = 'student', _('Student')

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    is_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT


class AuditLog(models.Model):
    """Track all significant system activities"""

    class Action(models.TextChoices):
        LOGIN = 'login', _('Login')
        LOGOUT = 'logout', _('Logout')
        CREATE = 'create', _('Create')
        UPDATE = 'update', _('Update')
        DELETE = 'delete', _('Delete')
        VIEW = 'view', _('View')
        ENROLL = 'enroll', _('Enroll')
        GRADE = 'grade', _('Grade')
        UPLOAD = 'upload', _('Upload')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='audit_logs')
    action = models.CharField(max_length=20, choices=Action.choices)
    resource = models.CharField(max_length=100, blank=True, help_text='Resource/model affected')
    resource_id = models.CharField(max_length=50, blank=True, help_text='ID of affected resource')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"


class LoginAnomaly(models.Model):
    """Track suspicious login patterns"""

    class Reason(models.TextChoices):
        MULTIPLE_FAILS = 'multiple_fails', _('Multiple Failed Attempts')
        NEW_LOCATION = 'new_location', _('New Location/IP')
        UNUSUAL_TIME = 'unusual_time', _('Unusual Login Time')
        NEW_DEVICE = 'new_device', _('New Device')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_anomalies')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    reason = models.CharField(max_length=30, choices=Reason.choices)
    flagged_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-flagged_at']
        verbose_name = 'Login Anomaly'
        verbose_name_plural = 'Login Anomalies'

    def __str__(self):
        return f"{self.user.email} - {self.reason} - {self.flagged_at}"
