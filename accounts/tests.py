"""Comprehensive tests for SUMS API"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin', email='admin@test.com',
            password='Admin@1234', first_name='Admin', last_name='User', role='admin'
        )
        self.student = User.objects.create_user(
            username='student1', email='student@test.com',
            password='Student@1234', first_name='John', last_name='Doe', role='student'
        )
        self.teacher = User.objects.create_user(
            username='teacher1', email='teacher@test.com',
            password='Teacher@1234', first_name='Prof', last_name='Smith', role='teacher'
        )

    def test_register(self):
        response = self.client.post('/api/auth/register/', {
            'email': 'new@test.com', 'username': 'newuser',
            'first_name': 'New', 'last_name': 'User',
            'role': 'student', 'password': 'New@12345', 'password_confirm': 'New@12345'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)

    def test_login(self):
        response = self.client.post('/api/auth/login/', {
            'email': 'student@test.com', 'password': 'Student@1234'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)

    def test_login_wrong_password(self):
        response = self.client.post('/api/auth/login/', {
            'email': 'student@test.com', 'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_auth(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_authenticated(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'student@test.com')

    def test_change_password(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/auth/change-password/', {
            'old_password': 'Student@1234',
            'new_password': 'NewStudent@5678',
            'new_password_confirm': 'NewStudent@5678'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_list_requires_admin(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/auth/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_list(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/auth/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CourseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin2', email='admin2@test.com',
            password='Admin@1234', first_name='Admin', last_name='User', role='admin'
        )
        self.student = User.objects.create_user(
            username='stu2', email='stu2@test.com',
            password='Stu@1234', first_name='Jane', last_name='Doe', role='student'
        )
        self.teacher = User.objects.create_user(
            username='tch2', email='tch2@test.com',
            password='Tch@1234', first_name='Prof', last_name='Jones', role='teacher'
        )

    def test_create_department_requires_admin(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/courses/departments/', {'name': 'CS', 'code': 'CSE'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_department_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/courses/departments/', {
            'name': 'Computer Science', 'code': 'CSE', 'description': 'CS department'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_departments_authenticated(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/courses/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_departments_unauthenticated(self):
        response = self.client.get('/api/courses/departments/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AttendanceTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='tch3', email='tch3@test.com',
            password='Tch@1234', first_name='Prof', last_name='Brown', role='teacher'
        )
        self.student = User.objects.create_user(
            username='stu3', email='stu3@test.com',
            password='Stu@1234', first_name='Bob', last_name='Smith', role='student'
        )

    def test_my_attendance_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/attendance/my-attendance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attendance_summary', response.data)

    def test_bulk_mark_requires_teacher(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/attendance/bulk-mark/', {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class NoticeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin3', email='admin3@test.com',
            password='Admin@1234', first_name='Admin', last_name='Three', role='admin'
        )
        self.student = User.objects.create_user(
            username='stu4', email='stu4@test.com',
            password='Stu@1234', first_name='Alice', last_name='Wang', role='student'
        )

    def test_create_notice_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/notices/', {
            'title': 'Test Notice', 'content': 'Test content', 'target_role': 'all'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_notice_as_student_denied(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/notices/', {
            'title': 'Illegal Notice', 'content': 'Nope', 'target_role': 'all'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_notices_as_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/notices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            username='stu5', email='stu5@test.com',
            password='Stu@1234', first_name='Sam', last_name='Lee', role='student'
        )
        self.teacher = User.objects.create_user(
            username='tch5', email='tch5@test.com',
            password='Tch@1234', first_name='Prof', last_name='Kim', role='teacher'
        )

    def test_chatbot_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/ai/chatbot/', {'question': 'How is CGPA calculated?'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('answer', response.data)

    def test_chatbot_no_question(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/ai/chatbot/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_students_teacher_only(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/ai/weak-students/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_weak_students_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/ai/weak-students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reputation_score(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/ai/reputation-score/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reputation_score', response.data)
