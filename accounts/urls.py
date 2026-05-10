from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Profile
    path('me/', views.MeView.as_view(), name='me'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),

    # Admin
    path('admin/users/', views.AdminUserViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin_users'),
    path('admin/users/<int:pk>/', views.AdminUserViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='admin_user_detail'),
    path('admin/audit-logs/', views.AuditLogListView.as_view(), name='audit_logs'),
    path('admin/login-anomalies/', views.LoginAnomalyView.as_view(), name='login_anomalies'),
]
