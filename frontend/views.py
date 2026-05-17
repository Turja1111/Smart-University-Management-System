from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def root_redirect(_: HttpRequest) -> HttpResponse:
    return redirect("login")


def login_page(request: HttpRequest) -> HttpResponse:
    return render(request, "auth/login.html", {"page_js": "js/pages/login.js"})


def register_page(request: HttpRequest) -> HttpResponse:
    return render(request, "auth/register.html", {"page_js": "js/pages/register.js"})


def student_dashboard(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "student/dashboard.html",
        {"page_js": "js/pages/student-dashboard.js"},
    )


def student_profile(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "student/profile.html",
        {"page_js": "js/pages/student-profile.js"},
    )


def student_attendance(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "student/attendance.html",
        {"page_js": "js/pages/student-attendance.js"},
    )


def student_exams(request: HttpRequest) -> HttpResponse:
    return render(request, "student/exams.html", {"page_js": "js/pages/student-exams.js"})


def student_grade_sheet(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "student/grade-sheet.html",
        {"page_js": "js/pages/student-grade-sheet.js"},
    )


def student_advising(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "student/advising.html",
        {"page_js": "js/pages/student-advising.js"},
    )


def teacher_dashboard(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "teacher/dashboard.html",
        {"page_js": "js/pages/teacher-dashboard.js"},
    )


def teacher_attendance(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "teacher/attendance.html",
        {"page_js": "js/pages/teacher-attendance.js"},
    )


def teacher_grades(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "teacher/grades.html",
        {"page_js": "js/pages/teacher-grades.js"},
    )


def admin_dashboard(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "admin/dashboard.html",
        {"page_js": "js/pages/admin-dashboard.js"},
    )


def admin_users(request: HttpRequest) -> HttpResponse:
    return render(request, "admin/users.html", {"page_js": "js/pages/admin-users.js"})


def admin_departments(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "admin/departments.html",
        {"page_js": "js/pages/admin-departments.js"},
    )


def admin_courses(request: HttpRequest) -> HttpResponse:
    return render(request, "admin/courses.html", {"page_js": "js/pages/admin-courses.js"})


def shared_courses(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "shared/courses.html",
        {"page_js": "js/pages/shared-courses.js"},
    )


def shared_notices(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "shared/notices.html",
        {"page_js": "js/pages/shared-notices.js"},
    )


def shared_ai(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "shared/ai_tools.html",
        {"page_js": "js/pages/shared-ai.js"},
    )

