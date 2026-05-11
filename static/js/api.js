import { getRefreshToken, getToken, logout, setTokens, setUser } from "./auth.js";

const API_BASE = "/api";

function headers() {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function refreshToken() {
  const refresh = getRefreshToken();
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    setTokens({ access: data.access });
    return true;
  } catch {
    return false;
  }
}

async function request(method, endpoint, data) {
  const opts = { method, headers: headers() };
  if (data !== undefined) opts.body = JSON.stringify(data);

  let res = await fetch(`${API_BASE}${endpoint}`, opts);
  if (res.status === 401) {
    const ok = await refreshToken();
    if (!ok) {
      logout();
      return null;
    }
    res = await fetch(`${API_BASE}${endpoint}`, { ...opts, headers: headers() });
  }

  const text = await res.text();
  const json = text ? JSON.parse(text) : {};
  if (!res.ok) {
    const err = new Error(json?.detail || "Request failed");
    err.status = res.status;
    err.data = json;
    throw err;
  }
  return json;
}

export const api = {
  get: (ep) => request("GET", ep),
  post: (ep, d) => request("POST", ep, d),
  put: (ep, d) => request("PUT", ep, d),
  patch: (ep, d) => request("PATCH", ep, d),
  delete: (ep) => request("DELETE", ep),

  auth: {
    login: (d) => api.post("/auth/login/", d),
    register: (d) => api.post("/auth/register/", d),
    logout: (d) => api.post("/auth/logout/", d),
    me: () => api.get("/auth/me/"),
    updateMe: (d) => api.patch("/auth/me/", d),
  },
  students: {
    profile: () => api.get("/students/profile/"),
    updateProfile: (d) => api.patch("/students/profile/", d),
    cgpa: () => api.get("/students/cgpa/"),
    routine: () => api.get("/students/routine/"),
  },
  teachers: {
    profile: () => api.get("/teachers/profile/"),
    myCourses: () => api.get("/teachers/my-courses/"),
    analytics: (id) => api.get(`/teachers/exam-analytics/${id}/`),
  },
  courses: {
    list: () => api.get("/courses/courses/"),
    departments: () => api.get("/courses/departments/"),
    enroll: (courseId) => api.post("/courses/enrollments/", { course: courseId }),
    assignments: () => api.get("/courses/assignments/"),
    submissions: () => api.get("/courses/submissions/"),
    grade: (id, d) => api.post(`/courses/submissions/${id}/grade/`, d),
  },
  attendance: {
    myAttendance: () => api.get("/attendance/my-attendance/"),
    bulkMark: (d) => api.post("/attendance/bulk-mark/", d),
  },
  exams: {
    myResults: () => api.get("/exams/my-results/"),
  },
  notices: {
    list: () => api.get("/notices/"),
    create: (d) => api.post("/notices/", d),
  },
  ai: {
    chatbot: (q) => api.post("/ai/chatbot/", { question: q }),
    weakStudents: () => api.get("/ai/weak-students/"),
    reputation: () => api.get("/ai/reputation-score/"),
    summary: (id) => api.post(`/ai/assignment-summary/${id}/`, {}),
    plagiarism: (id) => api.post(`/ai/plagiarism-check/${id}/`, {}),
  },
  admin: {
    users: () => api.get("/auth/admin/users/"),
    auditLogs: () => api.get("/auth/admin/audit-logs/"),
    anomalies: () => api.get("/auth/admin/login-anomalies/"),
    deleteUser: (id) => api.delete(`/auth/admin/users/${id}/`),
    updateUser: (id, d) => api.patch(`/auth/admin/users/${id}/`, d),
  },
};

export async function ensureMeLoaded() {
  const me = await api.auth.me();
  if (me) setUser(me);
  return me;
}

