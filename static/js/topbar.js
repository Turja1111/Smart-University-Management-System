import { getDisplayName, getInitials, getRole, getUser, isLoggedIn, logout } from "./auth.js";

const TITLES = {
  "/student/dashboard/": "Dashboard",
  "/student/attendance/": "My Attendance",
  "/student/exams/": "Results & Exams",
  "/teacher/dashboard/": "Dashboard",
  "/teacher/attendance/": "Mark Attendance",
  "/teacher/grades/": "Grade Submissions",
  "/admin-panel/dashboard/": "System Overview",
  "/admin-panel/users/": "User Management",
  "/admin-panel/departments/": "Departments & Courses",
  "/courses/": "Courses",
  "/notices/": "Notice Board",
  "/ai/": "AI Tools",
};

export function initTopbar() {
  if (window.location.pathname === "/login/" || window.location.pathname === "/register/") return;

  if (!isLoggedIn()) {
    window.location.href = "/login/";
    return;
  }

  document.getElementById("page-title").textContent = TITLES[window.location.pathname] || "SUMS";
  const role = getRole() || "student";
  document.getElementById("breadcrumb").textContent = `SUMS · ${role.charAt(0).toUpperCase() + role.slice(1)}`;

  document.getElementById("topbar-avatar-btn").textContent = getInitials();
  document.getElementById("dropdown-profile-name").textContent = getDisplayName();
  document.getElementById("dropdown-profile-email").textContent = getUser()?.email || "";

  document.getElementById("sidebar-toggle-btn")?.addEventListener("click", () => {
    document.getElementById("sidebar")?.classList.toggle("collapsed");
    document.getElementById("app-shell")?.classList.toggle("sidebar-collapsed");
  });

  const avatarBtn = document.getElementById("topbar-avatar-btn");
  const menu = document.getElementById("avatar-menu");
  avatarBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    menu?.classList.toggle("hidden");
  });

  document.addEventListener("click", () => menu?.classList.add("hidden"));

  document.getElementById("notif-btn")?.addEventListener("click", () => {
    window.location.href = "/notices/";
  });

  document.getElementById("topbar-logout")?.addEventListener("click", logout);
}

initTopbar();

