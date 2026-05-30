# Smart University Management System

A full-stack university management system built with Django, Django REST Framework, PostgreSQL, JWT authentication, and server-rendered frontend pages. The project manages students, teachers, courses, advising, attendance, exams, notices, and AI-assisted academic insights from one role-based platform.

The repository is prepared for local development, Docker usage, and free Render deployment.

## Features

- Role-based dashboards for admin, teacher, and student users
- JWT authentication with refresh-token blacklisting
- Custom user model with admin, teacher, and student roles
- Student profile, course enrollment, advising, attendance, routine, and grade views
- Teacher course, attendance, grading, and advising tools
- Admin user, department, course, notice, and audit-log management
- Course routine import from `routine_extracted.json`
- Exam result and grade-point tracking
- Notices with role-based targeting
- AI endpoints for academic chatbot, weak-student detection, plagiarism-style checks, assignment summaries, and reputation scoring
- Swagger and ReDoc API documentation via drf-spectacular
- Production static file serving with WhiteNoise
- Optional Cloudinary media storage
- Render-ready `render.yaml`, `build.sh`, `Procfile`, and `runtime.txt`

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Django 5, Django REST Framework |
| Frontend | Django templates, CSS, vanilla JavaScript |
| Authentication | SimpleJWT, Argon2 password hashing |
| Database | PostgreSQL |
| Static files | WhiteNoise |
| Media storage | Local development or Cloudinary |
| API docs | drf-spectacular, Swagger UI, ReDoc |
| Background tasks | Celery with Redis, optional in production |
| Deployment | Render, Gunicorn, Docker |

## Project Structure

```text
accounts/          Custom user model, authentication, permissions, audit logs
ai_integration/    AI-assisted academic endpoints
attendance/        Attendance models and APIs
config/            Django project settings, URLs, WSGI/ASGI, Celery
courses/           Departments, courses, enrollments, advising, routine import
exams/             Exam and result management
frontend/          Server-rendered page routes
notifications/     Notices and async notification tasks
static/            CSS and JavaScript assets
students/          Student profile and academic APIs
teachers/          Teacher profile and teaching APIs
templates/         HTML templates for all dashboards and pages
```

## Main Pages

| Page | URL |
| --- | --- |
| Login | `/login/` |
| Register | `/register/` |
| Student dashboard | `/student/dashboard/` |
| Student profile | `/student/profile/` |
| Student attendance | `/student/attendance/` |
| Student grade sheet | `/student/grade-sheet/` |
| Student advising | `/student/advising/` |
| Teacher dashboard | `/teacher/dashboard/` |
| Teacher attendance | `/teacher/attendance/` |
| Teacher advising | `/teacher/advising/` |
| Admin dashboard | `/admin-panel/dashboard/` |
| Admin users | `/admin-panel/users/` |
| Admin courses | `/admin-panel/courses/` |
| Shared courses | `/courses/` |
| Notices | `/notices/` |
| AI tools | `/ai/` |
| Django admin | `/admin/` |
| Swagger API docs | `/api/docs/` |
| ReDoc API docs | `/api/redoc/` |

## API Overview

| Method | Endpoint | Description | Access |
| --- | --- | --- | --- |
| `POST` | `/api/auth/register/` | Register a user | Public |
| `POST` | `/api/auth/login/` | Login and receive JWT tokens | Public |
| `POST` | `/api/auth/logout/` | Logout and blacklist refresh token | Authenticated |
| `GET` | `/api/auth/me/` | Current user profile | Authenticated |
| `GET` | `/api/courses/departments/` | List departments | Authenticated |
| `GET` | `/api/courses/courses/` | List courses | Authenticated |
| `POST` | `/api/courses/enrollments/` | Enroll in a course | Student |
| `GET` | `/api/students/cgpa/` | Student CGPA analytics | Student |
| `GET` | `/api/students/routine/` | Student class routine | Student |
| `POST` | `/api/attendance/bulk-mark/` | Mark attendance in bulk | Teacher |
| `GET` | `/api/attendance/my-attendance/` | Student attendance history | Student |
| `POST` | `/api/exams/results/` | Add exam result | Teacher |
| `GET` | `/api/exams/my-results/` | Student exam results | Student |
| `POST` | `/api/notices/` | Create notice | Admin |
| `POST` | `/api/ai/chatbot/` | Academic chatbot | Authenticated |
| `GET` | `/api/ai/weak-students/` | At-risk student analysis | Teacher |
| `GET` | `/api/ai/reputation-score/` | Academic reputation score | Authenticated |
| `GET` | `/api/auth/admin/audit-logs/` | Audit logs | Admin |

For the complete API schema, run the project and open `/api/docs/`.

## Requirements

- Python 3.12+
- PostgreSQL
- Redis, optional for Celery background workers
- Cloudinary account, optional for production media uploads

## Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Important variables:

```env
SECRET_KEY=change-this-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require

REDIS_URL=

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

OPENAI_API_KEY=

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@sums.edu
```

For local development, `DEBUG=True` is fine. For deployment, set `DEBUG=False`, use a strong `SECRET_KEY`, and set `ALLOWED_HOSTS` plus `CSRF_TRUSTED_ORIGINS` to your deployed domain.

## Local Setup

1. Clone the repository.

```bash
git clone <your-repository-url>
cd "Smart University Management System"
```

2. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Configure `.env`.

```bash
cp .env.example .env
```

5. Apply migrations.

```bash
python manage.py migrate
```

6. Load the included routine data.

```bash
python manage.py load_routine --path routine_extracted.json --semester fall --year 2026
```

7. Create an admin user.

```bash
python manage.py createsuperuser
```

8. Start the development server.

```bash
python manage.py runserver
```

Open:

- App: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`
- Swagger: `http://127.0.0.1:8000/api/docs/`

## Running Tests

```bash
python manage.py test --settings=config.settings.development
```

## Routine Data

The repository includes `routine_extracted.json`, which is used by the `load_routine` management command to seed course routine data.

```bash
python manage.py load_routine --path routine_extracted.json --semester fall --year 2026
```

The Render build also runs this command after migrations.

## Deployment on Render

This project includes the files needed for Render deployment:

- `render.yaml`
- `build.sh`
- `Procfile`
- `runtime.txt`

### Option 1: Render Blueprint

1. Push the repository to GitHub.
2. In Render, choose **New > Blueprint**.
3. Select this repository.
4. Render reads `render.yaml`, creates the web service and PostgreSQL database, installs dependencies, collects static files, applies migrations, and starts Gunicorn.

### Option 2: Manual Render Web Service

Use these settings:

```text
Runtime: Python
Build Command: bash build.sh
Start Command: python -m gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

Required environment variables:

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<generate-a-secure-secret>
DATABASE_URL=<your-render-postgres-url>
ALLOWED_HOSTS=<your-app-name>.onrender.com
CSRF_TRUSTED_ORIGINS=https://<your-app-name>.onrender.com
```

Optional environment variables:

```env
REDIS_URL=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
OPENAI_API_KEY=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

On a free Render web service, Redis can be omitted. The production settings run Celery tasks inline when `REDIS_URL` is not set.

Render free PostgreSQL databases may expire after 30 days. Upgrade the database if you need persistent production data.

## Docker

Build and run:

```bash
docker-compose up --build
```

Apply migrations inside the web container:

```bash
docker-compose exec web python manage.py migrate
```

## Security Notes

- Do not commit `.env`.
- Do not commit real passwords, API keys, database URLs, or email credentials.
- Use `DEBUG=False` in production.
- Use HTTPS domains in `CSRF_TRUSTED_ORIGINS`.
- Rotate `SECRET_KEY` if it was ever exposed publicly.
- Create production users through the admin panel or registration flow instead of storing credentials in the README.

## License

No license file is currently included. Add a license before publishing if you want to define how others may use, modify, or distribute this project.

## Author

Smart University Management System project.
