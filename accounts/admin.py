from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AuditLog, LoginAnomaly


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_verified', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering = ['-date_joined']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('SUMS Info', {'fields': ('role', 'phone', 'profile_picture', 'is_verified')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('SUMS Info', {'fields': ('email', 'first_name', 'last_name', 'role', 'phone')}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource', 'ip_address', 'timestamp']
    list_filter = ['action', 'resource']
    search_fields = ['user__email', 'description', 'resource']
    readonly_fields = ['user', 'action', 'resource', 'resource_id', 'ip_address', 'user_agent', 'description', 'metadata', 'timestamp']
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False


@admin.register(LoginAnomaly)
class LoginAnomalyAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'reason', 'flagged_at', 'resolved']
    list_filter = ['reason', 'resolved']
    search_fields = ['user__email', 'ip_address']
    ordering = ['-flagged_at']
    actions = ['mark_resolved']

    def mark_resolved(self, request, queryset):
        queryset.update(resolved=True)
    mark_resolved.short_description = 'Mark selected as resolved'
