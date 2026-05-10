# Smart University Management System — Implementation Plan

An enterprise-grade AI-enabled university management platform built with Django + DRF, as specified in the project documentation.

## User Review Required

> [!IMPORTANT]
> This is a **large, multi-app Django project**. The full implementation will include ~13 Django apps, 10+ database models, Celery background tasks, JWT auth, and AI feature stubs. Building everything will take significant time.

> [!WARNING]
> **AI Features**: The PDF calls for AI features (weak student prediction, plagiarism detection, chatbot, assignment summary). These will be implemented as **stub endpoints with realistic mock responses** unless you provide actual API keys (e.g., OpenAI/Google Gemini). Please confirm if you have API keys available.

> [!NOTE]
> **Database**: The project uses **PostgreSQL** as the primary database. For local development, we'll configure it to optionally use SQLite if `DATABASE_URL` is not set, so you can run the project immediately without setting up PostgreSQL.

---

## Proposed Changes

### Project Root Structure

```
d:\Projects\Smart University Management System\
├── config/                  # Django project settings & URLs
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── accounts/                # Custom user model, auth, RBAC, audit logs
├── students/                # Student profiles & features
├── teachers/                # Teacher profiles & grading
├── courses/                 # Departments, courses, enrollments
├── exams/                   # Exam results & analytics
├── attendance/              # Attendance tracking
├── notifications/           # Notices & automated alerts
├── ai_integration/          # AI features (prediction, chatbot, plagiarism)
├── api/                     # DRF routers, serializers, API docs
├── templates/               # (minimal, API-first)
├── static/
├── media/
├── docker/
├── .github/workflows/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Procfile
└── .env.example
```

---

### Core Configuration (`config/`)

#### [NEW] `config/settings/base.py`
- Installed apps for all modules
- JWT auth via `djangorestframework-simplejwt`
- Argon2 password hasher
- Cloudinary storage for media
- WhiteNoise for static files
- Celery with Redis broker
- CORS headers configuration
- DRF default settings (pagination, throttling, auth)

#### [NEW] `config/settings/development.py`
- SQLite fallback if `DATABASE_URL` not set
- Debug=True, relaxed throttling

#### [NEW] `config/settings/production.py`
- PostgreSQL via `dj-database-url`
- Debug=False, strict throttling
- `ALLOWED_HOSTS` from env

#### [NEW] `config/celery.py`
- Celery app configuration with Redis broker

---

### Accounts App (`accounts/`)

**Models:**
- `User` — custom AbstractUser with `role` field (ADMIN / TEACHER / STUDENT), `is_verified`, created_at
- `AuditLog` — user, action, ip_address, timestamp, metadata JSON
- `LoginAnomaly` — user, ip, user_agent, flagged_at, reason

**Endpoints:**
- `POST /api/auth/register/` — register with role
- `POST /api/auth/login/` — JWT token pair
- `POST /api/auth/logout/` — blacklist refresh token
- `POST /api/auth/token/refresh/` — refresh access token
- `GET /api/auth/me/` — current user profile
- `GET /api/admin/audit-logs/` — admin only

---

### Courses App (`courses/`)

**Models:**
- `Department` — name, code, head_teacher FK
- `Course` — name, code, department FK, teacher FK, credits, schedule (JSON: days/times)
- `Enrollment` — student FK, course FK, enrolled_at, status

**Endpoints:**
- CRUD `/api/courses/departments/`
- CRUD `/api/courses/courses/`
- `POST /api/courses/enroll/` — student enrollment
- `DELETE /api/courses/enroll/{id}/` — drop course
- `GET /api/courses/schedule-conflicts/` — conflict detection

---

### Students App (`students/`)

**Models:**
- `StudentProfile` — user OneToOne, student_id, department FK, semester, cgpa, photo (Cloudinary)

**Endpoints:**
- `GET/PUT /api/students/profile/`
- `GET /api/students/my-courses/`
- `GET /api/students/cgpa/` — analytics with grade breakdown
- `GET /api/students/routine/` — class schedule

---

### Teachers App (`teachers/`)

**Models:**
- `TeacherProfile` — user OneToOne, employee_id, department FK, specialization, photo

**Endpoints:**
- `GET/PUT /api/teachers/profile/`
- `GET /api/teachers/my-courses/`
- `POST /api/teachers/grade/` — grade assignment/exam
- `GET /api/teachers/exam-analytics/{course_id}/` — class performance stats

---

### Attendance App (`attendance/`)

**Models:**
- `AttendanceRecord` — student FK, course FK, date, status (PRESENT/ABSENT/LATE), marked_by FK

**Endpoints:**
- `POST /api/attendance/mark/` — bulk mark attendance (teacher)
- `GET /api/attendance/my-attendance/` — student view
- `GET /api/attendance/course/{id}/` — teacher/admin view
- `GET /api/attendance/analytics/` — percentage stats

---

### Exams App (`exams/`)

**Models:**
- `ExamResult` — student FK, course FK, exam_type (MIDTERM/FINAL/QUIZ), marks_obtained, total_marks, grade, semester, graded_by FK

**Endpoints:**
- `POST /api/exams/results/` — create result (teacher/admin)
- `GET /api/exams/my-results/` — student view
- `GET /api/exams/course-results/{course_id}/` — teacher view
- `GET /api/exams/analytics/{course_id}/` — class analytics

---

### Notifications App (`notifications/`)

**Models:**
- `Notice` — title, content, target_role (ALL/STUDENT/TEACHER), created_by FK, created_at, is_published

**Endpoints:**
- `POST /api/notices/` — create notice (admin)
- `GET /api/notices/` — list notices (filtered by role)
- Celery task: `send_notice_task` — async distribution

---

### AI Integration App (`ai_integration/`)

**Endpoints (all with realistic mock + hook for real AI):**
- `GET /api/ai/weak-students/` — predict at-risk students based on attendance + grades
- `POST /api/ai/chatbot/` — academic chatbot query
- `POST /api/ai/assignment-summary/{id}/` — summarize assignment submission (Celery)
- `POST /api/ai/plagiarism-check/{id}/` — check plagiarism (Celery)
- `GET /api/ai/reputation-score/{student_id}/` — academic reputation score

---

### Assignments (part of courses or students app)

**Models:**
- `Assignment` — course FK, title, description, due_date, created_by FK
- `AssignmentSubmission` — assignment FK, student FK, file (Cloudinary), submitted_at, grade, feedback, ai_summary

---

### Deployment Files

#### [NEW] `Dockerfile`
```
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

#### [NEW] `docker-compose.yml`
- web (Django + Gunicorn)
- redis (redis:alpine)
- celery worker

#### [NEW] `Procfile`
```
web: gunicorn config.wsgi:application
worker: celery -A config worker -l info
```

#### [NEW] `.github/workflows/ci.yml`
- Lint + test on push to main

---

## Verification Plan

### Automated Tests
After setup, run:
```powershell
cd "d:\Projects\Smart University Management System"
python manage.py test --settings=config.settings.development
```

### Manual API Verification
After running `python manage.py runserver`:
1. Navigate to `http://127.0.0.1:8000/api/docs/` — Swagger UI should load
2. Register a user: `POST /api/auth/register/`
3. Login and get JWT: `POST /api/auth/login/`
4. Test role-based endpoints with Bearer token
5. Create a course, enroll a student, mark attendance, add exam result

### Migration Check
```powershell
python manage.py makemigrations --settings=config.settings.development
python manage.py migrate --settings=config.settings.development
```
All migrations should apply without errors.
