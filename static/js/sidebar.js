import { getDisplayName, getInitials, getRole, isLoggedIn, isVerified, renderNameWithBadge, logout, setUser } from "./auth.js?v=10";
import { api } from "./api.js?v=10";

const NAV = {
  student: [
    { icon: "🏠", label: "Dashboard", href: "/student/dashboard/" },
    { icon: "👤", label: "Profile", href: "/student/profile/" },
    { icon: "📚", label: "Courses", href: "/courses/" },
    { icon: "🎒", label: "My Enrollments", href: "/student/enrollments/" },
    { icon: "📅", label: "Attendance", href: "/student/attendance/" },
    { icon: "🧠", label: "Advising", href: "/student/advising/" },
    { icon: "📊", label: "Grade Sheet", href: "/student/grade-sheet/" },
    { icon: "📢", label: "Notices", href: "/notices/" },
    { icon: "🤖", label: "AI Tools", href: "/ai/" },
  ],
  teacher: [
    { icon: "🏠", label: "Dashboard", href: "/teacher/dashboard/" },
    { icon: "📚", label: "Courses", href: "/courses/" },
    { icon: "📅", label: "Attendance", href: "/teacher/attendance/" },
    { icon: "🧾", label: "Advising", href: "/teacher/advising/" },
    { icon: "📝", label: "Grades", href: "/teacher/grades/" },
    { icon: "📢", label: "Notices", href: "/notices/" },
    { icon: "🤖", label: "AI Tools", href: "/ai/" },
  ],
  admin: [
    { icon: "🏠", label: "Dashboard", href: "/admin-panel/dashboard/" },
    { icon: "👥", label: "Users", href: "/admin-panel/users/" },
    { icon: "🏛️", label: "Departments", href: "/admin-panel/departments/" },
    { icon: "📚", label: "Courses", href: "/admin-panel/courses/" },
    { icon: "📢", label: "Notices", href: "/notices/" },
    { icon: "🤖", label: "AI Tools", href: "/ai/" },
  ],
};

function activePath() {
  return window.location.pathname;
}

function renderNav(role, verified) {
  let links = NAV[role] || NAV.student;

  // Apply feature restrictions for unverified users (admins are always unrestricted)
  if (!verified && role !== "admin") {
    const restrictedLabels = {
      student: ["Advising", "Attendance", "Grade Sheet"],
      teacher: ["Attendance", "Grades"],
    };
    const toHide = restrictedLabels[role] || [];
    links = links.filter((l) => !toHide.includes(l.label));
  }

  const itemsHost = document.getElementById("nav-items");
  if (itemsHost) {
    itemsHost.innerHTML = links
      .map((l) => {
        const path = activePath();
        const isActive =
          l.href === "/student/profile/"
            ? path === "/student/profile/"
            : path === l.href;
        return `
          <a class="nav-item${isActive ? " active" : ""}" href="${l.href}">
            <span class="nav-icon">${l.icon}</span>
            <span class="nav-label">${l.label}</span>
          </a>
        `;
      })
      .join("");
  }
}

async function renderCompletedCourses(role) {
  if (role !== "student") return;
  const container = document.getElementById("sidebar-completed-courses-container");
  const itemsHost = document.getElementById("completed-courses-items");
  if (!container || !itemsHost) return;

  try {
    const res = await api.courses.myEnrollments();
    const list = res.results || res || [];
    const completed = list.filter((e) => e.status === "completed");
    
    if (completed.length > 0) {
      container.style.display = "block";
      itemsHost.innerHTML = completed
        .map((e) => {
          return `
            <a class="nav-item" href="/courses/" style="font-size: 0.9rem; padding: 8px 16px;">
              <span class="nav-icon" style="font-size: 1rem;">✅</span>
              <span class="nav-label">${e.course_code}</span>
            </a>
          `;
        })
        .join("");
    }
  } catch (err) {
    // silently fail
  }
}

function renderUserInfo(role, verified) {
  const avatar = document.getElementById("sidebar-avatar");
  if (avatar) avatar.textContent = getInitials();

  const nameEl = document.getElementById("sidebar-user-name");
  if (nameEl) nameEl.innerHTML = renderNameWithBadge(getDisplayName(), verified);

  const badge = document.getElementById("sidebar-role-badge");
  if (badge) {
    badge.className = `role-badge ${role}`;
    badge.textContent = role;
  }
}

export async function initSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar) return;

  // Skip on auth pages
  if (window.location.pathname === "/login/" || window.location.pathname === "/register/") return;

  // If no token at all, kick to login
  if (!isLoggedIn()) {
    window.location.href = "/login/";
    return;
  }

  // 1. Render immediately from whatever is cached (fast path)
  const cachedRole = getRole() || "student";
  const cachedVerified = isVerified();
  renderNav(cachedRole, cachedVerified);
  renderUserInfo(cachedRole, cachedVerified);
  renderCompletedCourses(cachedRole);
  document.getElementById("sidebar-logout-btn")?.addEventListener("click", logout);

  // 2. Fetch fresh user data in background and re-render to fix any stale cache
  try {
    const me = await api.auth.me();
    if (me) {
      setUser(me);
      const freshRole = me.role || "student";
      const freshVerified = me.is_verified === true;

      // Re-render nav with accurate role
      renderNav(freshRole, freshVerified);
      renderUserInfo(freshRole, freshVerified);
      renderCompletedCourses(freshRole);

      // If cached role was wrong (e.g. stale student token for an admin),
      // redirect to the correct dashboard
      if (cachedRole !== freshRole) {
        const dashboards = {
          admin: "/admin-panel/dashboard/",
          teacher: "/teacher/dashboard/",
          student: "/student/dashboard/",
        };
        const correct = dashboards[freshRole];
        if (correct && !window.location.pathname.startsWith(correct.replace(/\/$/, ""))) {
          window.location.href = correct;
        }
      }
    }
  } catch (_) {
    // If refresh fails silently (network), leave the cached render in place
  }
}

// Auto-init
initSidebar();
