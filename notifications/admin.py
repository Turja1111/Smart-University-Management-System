from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_role', 'department', 'created_by', 'is_published', 'is_urgent', 'created_at']
    list_filter = ['target_role', 'is_published', 'is_urgent']
    search_fields = ['title', 'content']
