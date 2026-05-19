from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notice(models.Model):
    class TargetRole(models.TextChoices):
        ALL = 'all', 'All Users'
        STUDENT = 'student', 'Students Only'
        TEACHER = 'teacher', 'Teachers Only'
        ADMIN = 'admin', 'Admin Only'

    title = models.CharField(max_length=300)
    content = models.TextField()
    target_role = models.CharField(max_length=10, choices=TargetRole.choices, default=TargetRole.ALL)
    department = models.ForeignKey(
        'courses.Department', on_delete=models.SET_NULL, null=True, blank=True,
        help_text='Leave blank for university-wide notice'
    )
    target_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='personal_notices', help_text='For personal notifications'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='notices')
    is_published = models.BooleanField(default=True)
    is_urgent = models.BooleanField(default=False)
    publish_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notice'
        verbose_name_plural = 'Notices'

    def __str__(self):
        return f"[{self.target_role.upper()}] {self.title}"
