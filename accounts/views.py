"""Accounts views - Authentication, user management, audit logs"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend

from .models import AuditLog, LoginAnomaly
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    AdminUserSerializer
)
from .permissions import IsAdmin, IsAdminOrTeacher

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login endpoint - returns JWT token pair with user info"""
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Log successful login
            user_email = request.data.get('email', '')
            try:
                user = User.objects.get(email=user_email)
                AuditLog.objects.create(
                    user=user,
                    action=AuditLog.Action.LOGIN,
                    ip_address=_get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    description=f'User {user_email} logged in successfully.',
                )
                # Detect anomalies (simple: new IP)
                _check_login_anomaly(user, request)
            except User.DoesNotExist:
                pass
        return response


class RegisterView(generics.CreateAPIView):
    """Register a new user account"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Create JWT tokens for immediate login
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Registration successful.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LogoutView(generics.GenericAPIView):
    """Logout - blacklist refresh token"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.Action.LOGOUT,
                ip_address=_get_client_ip(request),
                description=f'{request.user.email} logged out.',
            )
            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    """Get or update current user profile"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    """Change user password"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.UPDATE,
            resource='password',
            ip_address=_get_client_ip(request),
            description='Password changed.',
        )
        return Response({'message': 'Password changed successfully.'})


class AdminUserViewSet(viewsets.ModelViewSet):
    """Admin-only user management"""
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'is_active', 'is_verified']
    search_fields = ['email', 'first_name', 'last_name', 'username']

    def perform_create(self, serializer):
        user = serializer.save()
        password = self.request.data.get('password')
        if password:
            user.set_password(password)
        else:
            user.set_password('sums1234')  # Default password
        user.save()
        AuditLog.objects.create(
            user=self.request.user,
            action=AuditLog.Action.CREATE,
            resource='User',
            resource_id=str(user.id),
            description=f'Admin created user: {user.email}',
        )

    def perform_update(self, serializer):
        user = serializer.save()
        password = self.request.data.get('password')
        if password:
            user.set_password(password)
            user.save()

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            user=self.request.user,
            action=AuditLog.Action.DELETE,
            resource='User',
            resource_id=str(instance.id),
            description=f'Admin deleted user: {instance.email}',
        )
        instance.delete()


class AuditLogListView(generics.ListAPIView):
    """Admin-only audit log viewer"""
    permission_classes = [IsAdmin]
    filterset_fields = ['action', 'resource']

    def get_queryset(self):
        from .models import AuditLog
        return AuditLog.objects.select_related('user').all()

    def list(self, request, *args, **kwargs):
        from .models import AuditLog
        from .serializers import UserSerializer
        queryset = AuditLog.objects.select_related('user').all()[:100]
        data = [{
            'id': log.id,
            'user': log.user.email if log.user else 'Anonymous',
            'action': log.action,
            'resource': log.resource,
            'resource_id': log.resource_id,
            'ip_address': str(log.ip_address),
            'description': log.description,
            'timestamp': log.timestamp,
        } for log in queryset]
        return Response(data)


class LoginAnomalyView(generics.ListAPIView):
    """Admin view for login anomalies"""
    permission_classes = [IsAdmin]

    def list(self, request):
        anomalies = LoginAnomaly.objects.select_related('user').filter(resolved=False)[:50]
        data = [{
            'id': a.id,
            'user': a.user.email,
            'ip_address': str(a.ip_address),
            'reason': a.reason,
            'flagged_at': a.flagged_at,
            'resolved': a.resolved,
        } for a in anomalies]
        return Response(data)


# Helper functions
def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


def _check_login_anomaly(user, request):
    """Simple login anomaly detection based on IP"""
    ip = _get_client_ip(request)
    last_login_ips = AuditLog.objects.filter(
        user=user, action=AuditLog.Action.LOGIN
    ).exclude(ip_address__isnull=True).values_list('ip_address', flat=True)[:10]

    if last_login_ips.exists():
        recent_ips = set(str(i) for i in last_login_ips)
        if ip not in recent_ips:
            LoginAnomaly.objects.create(
                user=user,
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                reason=LoginAnomaly.Reason.NEW_LOCATION,
            )
