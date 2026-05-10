"""Middleware for automatic audit logging and request tracking"""
from .models import AuditLog


class AuditLogMiddleware:
    """Lightweight middleware - only logs write operations"""
    TRACKED_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}
    SKIP_PATHS = {'/admin/', '/api/schema/', '/api/docs/', '/api/redoc/', '/api/auth/login/', '/api/auth/logout/'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if (
                request.method in self.TRACKED_METHODS and
                request.user.is_authenticated and
                not any(request.path.startswith(p) for p in self.SKIP_PATHS) and
                response.status_code < 400
            ):
                action_map = {
                    'POST': AuditLog.Action.CREATE,
                    'PUT': AuditLog.Action.UPDATE,
                    'PATCH': AuditLog.Action.UPDATE,
                    'DELETE': AuditLog.Action.DELETE,
                }
                AuditLog.objects.create(
                    user=request.user,
                    action=action_map.get(request.method, AuditLog.Action.VIEW),
                    resource=request.path,
                    ip_address=self._get_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    description=f'{request.method} {request.path} → {response.status_code}',
                )
        except Exception:
            pass  # Never break the request
        return response

    def _get_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '127.0.0.1')
