/**
 * demo.js – Frontend-only demo mode for SUMS
 *
 * Activated by clicking "View Demo" on the login page.
 * Intercepts all /api/* fetch calls and returns realistic mock data so
 * recruiters can explore every dashboard without a live backend.
 *
 * The real authentication code (auth.js, api.js) is NEVER modified;
 * this module simply seeds localStorage with a fake token/user and
 * patches window.fetch before the app tries to use it.
 */

const DEMO_KEY = "sums_demo_mode";

export const DEMO_USERS = {
  student: {
    id: 1,
    email: "alex.johnson@university.edu",
    first_name: "Alex",
    last_name: "Johnson",
    role: "student",
    is_verified: true,
    date_joined: "2024-09-01T08:00:00Z",
  },
  teacher: {
    id: 2,
    email: "dr.smith@university.edu",
    first_name: "Dr. Sarah",
    last_name: "Smith",
    role: "teacher",
    is_verified: true,
    date_joined: "2023-01-15T08:00:00Z",
  },
  admin: {
    id: 3,
    email: "admin@university.edu",
    first_name: "System",
    last_name: "Admin",
    role: "admin",
    is_verified: true,
    date_joined: "2022-06-01T08:00:00Z",
  },
};

// ── Mock data keyed by endpoint ───────────────────────────────────────────────

const MOCK_RESPONSES = {
  "/api/auth/me/": (role) => DEMO_USERS[role] || DEMO_USERS.student,

  "/api/auth/token/refresh/": () => ({ access: "demo-access-token-refreshed" }),

  "/api/students/profile/": () => ({
    student_id: "STU-2024-001",
    department: "Computer Science & Engineering",
    semester: 6,
    batch: "2021",
    cgpa: 3.72,
    credits_completed: 108,
    advisor: "Dr. Sarah Smith",
    phone: "+880-1700-000001",
    address: "Dhaka, Bangladesh",
  }),

  "/api/students/cgpa/": () => ({
    cgpa: 3.72,
    current_cgpa: 3.72,
    semesters: ["S1", "S2", "S3", "S4", "S5", "S6"],
    values: [3.50, 3.55, 3.60, 3.80, 3.75, 3.72],
  }),

  "/api/students/routine/": () => ({
    by_day: {
      Monday: [
        { course_code: "CSE-301", course_name: "Data Structures", start_time: "08:00", end_time: "09:30", room: "201", kind: "Lecture" },
        { course_code: "CSE-303", course_name: "Algorithms", start_time: "10:00", end_time: "11:30", room: "Lab-3", kind: "Lab" },
      ],
      Tuesday: [
        { course_code: "CSE-305", course_name: "Database Systems", start_time: "09:00", end_time: "10:30", room: "105", kind: "Lecture" },
        { course_code: "MATH-201", course_name: "Discrete Mathematics", start_time: "11:00", end_time: "12:30", room: "202", kind: "Lecture" },
      ],
      Wednesday: [
        { course_code: "CSE-307", course_name: "Operating Systems", start_time: "08:30", end_time: "10:00", room: "301", kind: "Lecture" },
        { course_code: "CSE-303", course_name: "Algorithms", start_time: "13:00", end_time: "14:30", room: "203", kind: "Tutorial" },
      ],
      Thursday: [
        { course_code: "CSE-301", course_name: "Data Structures", start_time: "09:00", end_time: "10:30", room: "Lab-1", kind: "Lab" },
        { course_code: "CSE-305", course_name: "Database Systems", start_time: "11:00", end_time: "12:30", room: "105", kind: "Tutorial" },
      ],
      Friday: [
        { course_code: "MATH-201", course_name: "Discrete Mathematics", start_time: "10:00", end_time: "11:30", room: "202", kind: "Tutorial" },
      ],
      Saturday: [],
      Sunday: [],
    },
  }),

  "/api/courses/assignments/": () => ({
    results: [
      { id: 1, course_code: "CSE-301", title: "Binary Search Tree Implementation", due_date: "2026-08-10T23:59:00Z", is_submitted: true },
      { id: 2, course_code: "CSE-305", title: "ER Diagram Design", due_date: "2026-08-15T23:59:00Z", is_submitted: false },
      { id: 3, course_code: "CSE-303", title: "Sorting Algorithm Analysis", due_date: "2026-07-25T23:59:00Z", is_submitted: false },
      { id: 4, course_code: "MATH-201", title: "Graph Theory Problem Set", due_date: "2026-08-05T23:59:00Z", is_submitted: true },
    ],
  }),

  "/api/attendance/my-attendance/": () => ({
    results: [
      { course_code: "CSE-301", course_name: "Data Structures", total: 24, present: 22, percentage: 91.7 },
      { course_code: "CSE-303", course_name: "Algorithms", total: 20, present: 17, percentage: 85.0 },
      { course_code: "CSE-305", course_name: "Database Systems", total: 22, present: 19, percentage: 86.4 },
      { course_code: "CSE-307", course_name: "Operating Systems", total: 18, present: 12, percentage: 66.7 },
      { course_code: "MATH-201", course_name: "Discrete Mathematics", total: 20, present: 18, percentage: 90.0 },
    ],
  }),

  "/api/exams/my-results/": () => ({
    results: [
      { course_code: "CSE-201", course_name: "OOP with Java", semester: "Spring 2025", marks: 88, total_marks: 100, grade: "A", grade_points: 4.0, exam_type: "Final" },
      { course_code: "CSE-203", course_name: "Computer Networks", semester: "Spring 2025", marks: 76, total_marks: 100, grade: "B+", grade_points: 3.5, exam_type: "Final" },
      { course_code: "MATH-101", course_name: "Calculus I", semester: "Fall 2024", marks: 92, total_marks: 100, grade: "A+", grade_points: 4.0, exam_type: "Final" },
      { course_code: "CSE-101", course_name: "Intro to Programming", semester: "Fall 2024", marks: 85, total_marks: 100, grade: "A", grade_points: 4.0, exam_type: "Final" },
    ],
  }),

  "/api/courses/courses/": () => ({
    count: 6,
    results: [
      { id: 1, code: "CSE-301", name: "Data Structures", credits: 3, department: "CSE", teacher: "Dr. Alan Turing", enrolled: true },
      { id: 2, code: "CSE-303", name: "Algorithms", credits: 3, department: "CSE", teacher: "Dr. Grace Hopper", enrolled: true },
      { id: 3, code: "CSE-305", name: "Database Systems", credits: 3, department: "CSE", teacher: "Dr. Sarah Smith", enrolled: true },
      { id: 4, code: "CSE-307", name: "Operating Systems", credits: 3, department: "CSE", teacher: "Dr. Dennis Ritchie", enrolled: true },
      { id: 5, code: "MATH-201", name: "Discrete Mathematics", credits: 3, department: "MATH", teacher: "Prof. Euler", enrolled: true },
      { id: 6, code: "CSE-401", name: "Machine Learning", credits: 3, department: "CSE", teacher: "Dr. Geoffrey Hinton", enrolled: false },
    ],
  }),

  "/api/courses/departments/": () => ({
    results: [
      { id: 1, name: "Computer Science & Engineering", code: "CSE", courses_count: 24 },
      { id: 2, name: "Mathematics", code: "MATH", courses_count: 12 },
      { id: 3, name: "Physics", code: "PHY", courses_count: 10 },
      { id: 4, name: "Electrical Engineering", code: "EEE", courses_count: 18 },
    ],
  }),

  "/api/courses/enrollments/": () => ({
    results: [
      { id: 1, course_code: "CSE-301", course_name: "Data Structures", status: "enrolled", semester: "Fall 2026" },
      { id: 2, course_code: "CSE-303", course_name: "Algorithms", status: "enrolled", semester: "Fall 2026" },
      { id: 3, course_code: "CSE-305", course_name: "Database Systems", status: "enrolled", semester: "Fall 2026" },
      { id: 4, course_code: "CSE-201", course_name: "OOP with Java", status: "completed", semester: "Spring 2025" },
      { id: 5, course_code: "MATH-101", course_name: "Calculus I", status: "completed", semester: "Fall 2024" },
    ],
  }),

  "/api/notices/": () => ({
    results: [
      { id: 1, title: "Final Exam Schedule – Fall 2026", content: "Final examinations will be held from November 25 to December 5, 2026. Check the notice board for your individual schedule.", created_at: "2026-07-10T09:00:00Z", target_role: "all", author: "Admin Office" },
      { id: 2, title: "Mid-term Results Published", content: "Mid-term examination results for all departments are now available in the student portal. Please verify your grades.", created_at: "2026-07-08T11:00:00Z", target_role: "student", author: "Exam Committee" },
      { id: 3, title: "Campus Wi-Fi Maintenance", content: "Campus Wi-Fi will be temporarily unavailable on July 20, 2026 from 2:00 AM to 5:00 AM for scheduled maintenance.", created_at: "2026-07-05T08:00:00Z", target_role: "all", author: "IT Department" },
      { id: 4, title: "Research Seminar – AI in Education", content: "Join us for a research seminar on Artificial Intelligence in Higher Education on July 22, 2026, Room 301.", created_at: "2026-07-01T10:00:00Z", target_role: "teacher", author: "Research Cell" },
    ],
  }),

  "/api/ai/chatbot/": (_, body) => ({
    question: body?.question || "Demo question",
    answer: "This is a demo response from the SUMS AI Academic Assistant. In a live environment, this connects to an AI model for real-time academic guidance on CGPA, attendance, course enrollment, and exam scheduling.",
    response_by: "SUMS Academic AI Assistant (Demo)",
    timestamp: new Date().toISOString(),
    note: "Demo mode — connect OPENAI_API_KEY for live AI responses.",
  }),

  "/api/ai/reputation-score/": () => ({
    student: "Alex Johnson",
    email: "alex.johnson@university.edu",
    reputation_score: 78.5,
    rank: "Good",
    breakdown: { attendance_score: 25.8, academic_score: 42.2, assignment_score: 10.5 },
  }),

  "/api/ai/weak-students/": () => ({
    at_risk_students: [
      { student: "Mark Chen", email: "mark.chen@university.edu", course: "CSE-307", attendance_percentage: 63.2, average_grade_points: 1.8, risk_factors: ["Low attendance: 63.2%", "Low GPA: 1.80"], risk_level: "high" },
      { student: "Lisa Wong", email: "lisa.wong@university.edu", course: "CSE-303", attendance_percentage: 71.4, average_grade_points: 2.1, risk_factors: ["Low attendance: 71.4%"], risk_level: "medium" },
    ],
    total: 2,
    analysis_timestamp: new Date().toISOString(),
  }),

  "/api/teachers/profile/": () => ({
    employee_id: "TCH-2023-008",
    department: "Computer Science & Engineering",
    designation: "Associate Professor",
    specialization: "Database Systems, Distributed Computing",
    office_room: "Faculty Block B, Room 12",
    phone: "+880-1700-000002",
  }),

  "/api/teachers/my-courses/": () => ({
    results: [
      { id: 3, code: "CSE-305", name: "Database Systems", credits: 3, enrolled_count: 42, semester: "Fall 2026" },
      { id: 7, code: "CSE-502", name: "Advanced Database Design", credits: 3, enrolled_count: 28, semester: "Fall 2026" },
    ],
  }),

  "/api/auth/admin/users/": () => ({
    count: 5,
    results: [
      { id: 1, email: "alex.johnson@university.edu", first_name: "Alex", last_name: "Johnson", role: "student", is_verified: true, date_joined: "2024-09-01T08:00:00Z" },
      { id: 2, email: "dr.smith@university.edu", first_name: "Dr. Sarah", last_name: "Smith", role: "teacher", is_verified: true, date_joined: "2023-01-15T08:00:00Z" },
      { id: 3, email: "admin@university.edu", first_name: "System", last_name: "Admin", role: "admin", is_verified: true, date_joined: "2022-06-01T08:00:00Z" },
      { id: 4, email: "jane.doe@university.edu", first_name: "Jane", last_name: "Doe", role: "student", is_verified: false, date_joined: "2025-01-10T08:00:00Z" },
      { id: 5, email: "prof.jones@university.edu", first_name: "Prof. David", last_name: "Jones", role: "teacher", is_verified: true, date_joined: "2024-02-20T08:00:00Z" },
    ],
  }),

  "/api/auth/admin/audit-logs/": () => ({
    count: 3,
    results: [
      { id: 1, user: "admin@university.edu", action: "LOGIN", timestamp: new Date(Date.now() - 3600000).toISOString(), ip_address: "192.168.1.1" },
      { id: 2, user: "alex.johnson@university.edu", action: "PROFILE_UPDATE", timestamp: new Date(Date.now() - 7200000).toISOString(), ip_address: "192.168.1.42" },
      { id: 3, user: "dr.smith@university.edu", action: "ATTENDANCE_MARK", timestamp: new Date(Date.now() - 10800000).toISOString(), ip_address: "192.168.1.55" },
    ],
  }),

  "/api/auth/admin/login-anomalies/": () => ({ count: 0, results: [] }),

  "/api/courses/submissions/": () => ({
    results: [
      { id: 1, student: "Alex Johnson", assignment: "Binary Search Tree Implementation", course_code: "CSE-301", submitted_at: "2026-08-09T20:45:00Z", is_late: false, grade: 92, plagiarism_score: 4.2 },
    ],
  }),
};

// ── Helpers ───────────────────────────────────────────────────────────────────

function isDemoMode() {
  return localStorage.getItem(DEMO_KEY) === "1";
}

function getDemoRole() {
  return localStorage.getItem("sums_demo_role") || "student";
}

function makeResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function matchEndpoint(url) {
  const path = url.replace(window.location.origin, "").split("?")[0].replace(/\/$/, "") + "/";
  // Try exact match first
  for (const key of Object.keys(MOCK_RESPONSES)) {
    const normKey = key.replace(/\/$/, "") + "/";
    if (path === normKey) return MOCK_RESPONSES[key];
  }
  // Try prefix match for dynamic routes (e.g. /api/teachers/exam-analytics/3/)
  for (const key of Object.keys(MOCK_RESPONSES)) {
    if (path.startsWith(key.replace(/\/$/, ""))) return MOCK_RESPONSES[key];
  }
  return null;
}

// ── Fetch Interceptor ─────────────────────────────────────────────────────────

const _realFetch = window.fetch.bind(window);

function installInterceptor() {
  window.fetch = async function (input, init) {
    const url = typeof input === "string" ? input : input.url;

    if (!url.includes("/api/")) {
      return _realFetch(input, init);
    }

    const role = getDemoRole();
    let body = null;
    if (init?.body) {
      try { body = JSON.parse(init.body); } catch (_) {}
    }

    const handler = matchEndpoint(url);
    if (handler) {
      await new Promise((r) => setTimeout(r, 120)); // realistic latency
      return makeResponse(handler(role, body));
    }

    // Unknown /api/ endpoint – return 200 empty
    return makeResponse({});
  };
}

// ── Demo Activation ───────────────────────────────────────────────────────────

export function activateDemo(role = "student") {
  localStorage.setItem(DEMO_KEY, "1");
  localStorage.setItem("sums_demo_role", role);

  const user = DEMO_USERS[role] || DEMO_USERS.student;
  localStorage.setItem("sums_user", JSON.stringify(user));
  localStorage.setItem("access_token", "demo-access-token");
  localStorage.setItem("refresh_token", "demo-refresh-token");

  installInterceptor();
}

export function deactivateDemo() {
  localStorage.removeItem(DEMO_KEY);
  localStorage.removeItem("sums_demo_role");
  localStorage.removeItem("sums_user");
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.fetch = _realFetch;
}

// ── Auto-init: restore interceptor on page load if already in demo mode ───────

if (isDemoMode()) {
  installInterceptor();

  // Show demo banner after DOM is ready
  function showBanner() {
    const role = getDemoRole();
    const banner = document.getElementById("demo-banner");
    if (banner) {
      banner.style.display = "flex";
      const roleLabel = document.getElementById("demo-banner-role");
      if (roleLabel) roleLabel.textContent = role.charAt(0).toUpperCase() + role.slice(1);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", showBanner);
  } else {
    showBanner();
  }
}
