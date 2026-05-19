from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users"""
    message = 'Admin access required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsTeacher(permissions.BasePermission):
    """Allow access only to teacher users"""
    message = 'Teacher access required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_teacher)


class IsVerifiedTeacher(permissions.BasePermission):
    """Allow access only to verified teacher users"""
    message = 'Verified Teacher access required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_teacher and request.user.is_verified)


class IsStudent(permissions.BasePermission):
    """Allow access only to student users"""
    message = 'Student access required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_student)


class IsAdminOrTeacher(permissions.BasePermission):
    """Allow access to admin or teacher users"""
    message = 'Admin or Teacher access required.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_admin or request.user.is_teacher)
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access if owner of the object or admin"""
    message = 'You do not have permission to access this resource.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        # Check for user attribute on the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'student'):
            return obj.student.user == request.user
        return obj == request.user


class ReadOnlyOrAdmin(permissions.BasePermission):
    """Read for authenticated, write for admin"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_admin
