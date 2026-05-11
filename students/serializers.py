from rest_framework import serializers
from .models import StudentProfile
from courses.models import Enrollment


class StudentProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_phone = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'user_email', 'user_name', 'user_phone', 'student_id', 'department',
            'department_name', 'semester', 'batch', 'cgpa', 'total_credits_completed',
            'date_of_birth', 'address', 'emergency_contact_name', 'emergency_contact',
            'birth_certificate_no', 'passport_no', 'admission_session', 'created_at',
        ]
        read_only_fields = ['user', 'cgpa', 'total_credits_completed', 'created_at']

    def get_user_email(self, obj):
        return obj.user.email

    def get_user_name(self, obj):
        return obj.user.get_full_name()

    def get_user_phone(self, obj):
        return obj.user.phone or ''

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None


class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = [
            'semester', 'batch', 'date_of_birth', 'address',
            'emergency_contact_name', 'emergency_contact',
            'birth_certificate_no', 'passport_no', 'admission_session',
        ]


class CGPAAnalyticsSerializer(serializers.Serializer):
    cgpa = serializers.FloatField()
    total_credits = serializers.IntegerField()
    completed_courses = serializers.IntegerField()
    grade_distribution = serializers.DictField()
    semester_performance = serializers.ListField()
