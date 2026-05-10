# Smart University Management System (SUMS)

> An enterprise-grade, AI-enabled university management platform built with Django + Django REST Framework.

---

## 🚀 Quick Start (Local Development)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Create a superuser (already done: admin@sums.edu / Admin@1234)
python manage.py createsuperuser

# 4. Start the development server
python manage.py runserver

# 5. Open API documentation
# http://127.0.0.1:8000/api/docs/   ← Swagger UI
# http://127.0.0.1:8000/admin/      ← Django Admin
```

---

## 🧱 Project Structure

```
config/               ← Django project settings (base/dev/prod)
accounts/             ← Custom user model, JWT auth, RBAC, audit logs
students/             ← Student profiles, CGPA analytics, routine
teachers/             ← Teacher profiles, grading, exam analytics
courses/              ← Departments, courses, enrollments, assignments
attendance/           ← Attendance records, bulk marking, analytics
exams/                ← Exam results with auto grade calculation
notifications/        ← Notices with role-based targeting, Celery
ai_integration/       ← Chatbot, weak student prediction, plagiarism, reputation score
```

---

## 🔐 User Roles & Credentials

| Role    | Email                 | Password    |
|---------|-----------------------|-------------|
| Admin   | admin@sums.edu        | Admin@1234  |

Register new teachers/students via `POST /api/auth/register/`.

---

## 📡 Key API Endpoints

| Method | Endpoint                            | Description                     | Role       |
|--------|-------------------------------------|---------------------------------|------------|
| POST   | `/api/auth/register/`               | Register new user               | Public     |
| POST   | `/api/auth/login/`                  | Login → JWT tokens              | Public     |
| POST   | `/api/auth/logout/`                 | Blacklist refresh token         | Auth       |
| GET    | `/api/auth/me/`                     | Current user profile            | Auth       |
| GET    | `/api/courses/departments/`         | List departments                | Auth       |
| GET    | `/api/courses/courses/`             | List courses                    | Auth       |
| POST   | `/api/courses/enrollments/`         | Enroll in course                | Student    |
| GET    | `/api/students/cgpa/`               | CGPA analytics                  | Student    |
| GET    | `/api/students/routine/`            | Class schedule                  | Student    |
| POST   | `/api/attendance/bulk-mark/`        | Bulk mark attendance            | Teacher    |
| GET    | `/api/attendance/my-attendance/`    | Personal attendance             | Student    |
| POST   | `/api/exams/results/`               | Add exam result                 | Teacher    |
| GET    | `/api/exams/my-results/`            | Student's results               | Student    |
| POST   | `/api/notices/`                     | Create notice                   | Admin      |
| POST   | `/api/ai/chatbot/`                  | Academic chatbot                | Auth       |
| GET    | `/api/ai/weak-students/`            | At-risk student prediction      | Teacher    |
| GET    | `/api/ai/reputation-score/`         | Academic reputation score       | Auth       |
| GET    | `/api/auth/admin/audit-logs/`       | Audit log viewer                | Admin      |
| GET    | `/api/docs/`                        | Swagger API documentation       | Public     |

---

## 🤖 AI Features

All AI endpoints are fully functional with **intelligent mock responses** and are architected to plug into a real AI backend:

- **Chatbot**: Keyword-aware responses. Set `OPENAI_API_KEY` for full LLM responses.
- **Weak Student Prediction**: Analyzes real attendance + grade data.
- **Assignment Summary**: Summarizes submission text, extensible to LLM.
- **Plagiarism Detection**: Cross-checks submissions, extensible to APIs.
- **Reputation Score**: 100-point score from attendance (30) + grades (50) + assignments (20).

---

## 🛡️ Security Features

- JWT authentication with refresh token blacklisting on logout
- Argon2 password hashing
- RBAC permission classes (`IsAdmin`, `IsTeacher`, `IsStudent`)
- API rate throttling (100/hr anonymous, 1000/hr authenticated)
- Automatic audit logging middleware (all write operations)
- Login anomaly detection (new IP flagging)

---

## ⚙️ Environment Variables (`.env`)

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=          # blank = SQLite (dev), or postgres:// for prod
REDIS_URL=redis://localhost:6379/0
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
OPENAI_API_KEY=        # optional, for real AI responses
```

---

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Apply migrations inside container
docker-compose exec web python manage.py migrate
```

## ☁️ Render Deployment

1. Push to GitHub
2. Create a new Web Service on [render.com](https://render.com)
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn config.wsgi:application`
5. Add environment variables (see `.env.example`)
6. Add a Neon PostgreSQL database and set `DATABASE_URL`

---

## 🧪 Running Tests

```bash
python manage.py test accounts --settings=config.settings.development
# Ran 22 tests in 3.071s - OK ✅
```

---

## 📦 Tech Stack

| Layer        | Technology                                |
|--------------|-------------------------------------------|
| Backend      | Django 5.0, Django REST Framework 3.15    |
| Auth         | JWT (SimpleJWT) + Argon2 hashing          |
| Database     | PostgreSQL (via `DATABASE_URL`)           |
| Cache/Queue  | Redis + Celery                            |
| Storage      | Local (dev) / Cloudinary (prod)           |
| Static Files | WhiteNoise                                |
| API Docs     | drf-spectacular (Swagger + ReDoc)         |
| Deployment   | Docker, Gunicorn, Nginx, Render           |
| CI/CD        | GitHub Actions                            |
