import { getDisplayName, getInitials, getRole, isLoggedIn, logout } from "./auth.js";

const NAV = {
  student: [
    { icon: "🏠", label: "Dashboard", href: "/student/dashboard/" },
    { icon: "📚", label: "Courses", href: "/courses/" },
    { icon: "📅", label: "Attendance", href: "/student/attendance/" },
    { icon: "📊", label: "Results", href: "/student/exams/" },
    { icon: "📢", label: "Notices", href: "/notices/" },
    { icon: "🤖", label: "AI Tools", href: "/ai/" },
  ],
  teacher: [
    { icon: "🏠", label: "Dashboard", href: "/teacher/dashboard/" },
    { icon: "📚", label: "Courses", href: "/courses/" },
    { icon: "📅", label: "Attendance", href: "/teacher/attendance/" },
    { icon: "📝", label: "Grades", href: "/teacher/grades/" },
    { icon: "📢", label: "Notices", href: "/notices/" },
    { icon: "🤖", label: "AI Tools", href: "/ai/" },
  ],
  admin: [
    { icon: "🏠", label: "Dashboard", href: "/admin-panel/dashboard/" },
    { icon: "👥", label: "Users", href: "/admin-panel/users/" },
    { icon: "🏛️", label: "Departments", href: "/admin-panel/departments/" },
    { icon: "📚", label: "Courses", href: "/courses/" },
    { icon: "📢", label: "Notices", href: "/notices/" },
    { icon: "🤖", label: "AI Tools", href: "/ai/" },
  ],
};

function activePath() {
  return window.location.pathname;
}

export function initSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar) return;

  // Hide shell on auth pages
  if (window.location.pathname === "/login/" || window.location.pathname === "/register/") return;

  // If not logged in, kick to login
  if (!isLoggedIn()) {
    window.location.href = "/login/";
    return;
  }

  const role = getRole() || "student";
  const links = NAV[role] || NAV.student;
  const itemsHost = document.getElementById("nav-items");
  if (itemsHost) {
    itemsHost.innerHTML = links
      .map((l) => {
        const isActive = activePath() === l.href;
        return `
          <a class="nav-item${isActive ? " active" : ""}" href="${l.href}">
            <span class="nav-icon">${l.icon}</span>
            <span class="nav-label">${l.label}</span>
          </a>
        `;
      })
      .join("");
  }

  document.getElementById("sidebar-avatar").textContent = getInitials();
  document.getElementById("sidebar-user-name").textContent = getDisplayName();
  const badge = document.getElementById("sidebar-role-badge");
  if (badge) {
    badge.className = `role-badge ${role}`;
    badge.textContent = role;
  }

  document.getElementById("sidebar-logout-btn")?.addEventListener("click", logout);
}

// Auto-init
initSidebar();

