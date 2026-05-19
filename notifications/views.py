"""Notifications views"""
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers as drf_serializers

from .models import Notice
from accounts.permissions import IsAdmin


class NoticeSerializer(drf_serializers.ModelSerializer):
    created_by_name = drf_serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = ['id', 'title', 'content', 'target_role', 'department',
                  'created_by', 'created_by_name', 'is_published', 'is_urgent',
                  'publish_at', 'expires_at', 'created_at']
        read_only_fields = ['created_by', 'publish_at', 'created_at']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else 'System'


class NoticeViewSet(viewsets.ModelViewSet):
    serializer_class = NoticeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Notice.objects.all().select_related('created_by', 'department')
        # Students/Teachers see notices targeted at them specifically, or general notices for their role
        from django.db.models import Q
        return Notice.objects.filter(
            Q(target_user=user) | Q(target_user__isnull=True, target_role__in=['all', user.role]),
            is_published=True
        ).select_related('created_by', 'department')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        notice = serializer.save(created_by=self.request.user)
        # Trigger async notification task
        try:
            from .tasks import send_notice_task
            send_notice_task.delay(notice.id)
        except Exception:
            pass  # Celery not available
