from rest_framework import serializers
from .models import TeacherProfile


class TeacherProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    courses_count = serializers.SerializerMethodField()

    class Meta:
        model = TeacherProfile
        fields = ['id', 'user', 'user_email', 'user_name', 'employee_id', 'department',
                  'department_name', 'specialization', 'qualification', 'designation',
                  'bio', 'date_of_joining', 'office_room', 'courses_count', 'created_at']
        read_only_fields = ['user', 'created_at']

    def get_user_email(self, obj):
        return obj.user.email

    def get_user_name(self, obj):
        return obj.user.get_full_name()

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_courses_count(self, obj):
        return obj.user.teaching_courses.filter(is_active=True).count()
