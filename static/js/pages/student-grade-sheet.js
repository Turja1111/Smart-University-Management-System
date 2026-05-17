/**
 * student-grade-sheet.js
 * Grade Sheet page — loads grades, renders table, generates PDF via jsPDF
 */
import { api, ensureMeLoaded } from "../api.js";
import { getUser, getRole } from "../auth.js";
import { toast } from "../toast.js";

// ─── State ────────────────────────────────────────────────────────────────────
let state = {
  profile: null,
  cgpa: null,
  results: [],
  me: null,
  filteredSemester: "All",
};

// ─── Utility helpers ──────────────────────────────────────────────────────────
function dash(v) {
  if (v === null || v === undefined || v === "") return "—";
  return String(v);
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function hide(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add("hidden");
}

function show(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove("hidden");
}

function pctColor(pct) {
  if (pct >= 85) return "#10b981";
  if (pct >= 70) return "#3b82f6";
  if (pct >= 55) return "#f59e0b";
  return "#ef4444";
}

function gradeClass(grade) {
  const map = {
    "A+": "A-plus",
    "A":  "A",
    "A-": "A-minus",
    "B+": "B-plus",
    "B":  "B",
    "B-": "B-minus",
    "C+": "C-plus",
    "C":  "C",
    "D":  "D",
    "F":  "F",
  };
  return map[grade] || "default";
}

function semesterLabel(r) {
  const sem = r.semester || "";
  const year = r.year || "";
  if (!sem && !year) return "—";
  return `${sem.toUpperCase()} ${year}`.trim();
}

// ─── Render student info card ──────────────────────────────────────────────────
function renderInfo() {
  const p = state.profile;
  const me = state.me;
  const c = state.cgpa;

  if (!p && !me) return;

  const fullName = p?.user_name || me?.full_name || `${me?.first_name || ""} ${me?.last_name || ""}`.trim() || "Student";
  const initials = fullName
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  setText("gs-student-name", fullName);
  setText("gs-student-id", dash(p?.student_id));
  setText("gs-department", dash(p?.department_name));
  setText("gs-batch", dash(p?.batch));
  setText("gs-avatar-initials", initials || "S");

  // Program = Department + "BACHELOR OF SCIENCE IN COMPUTER SCIENCE AND ENGINEERING" style
  // We try to build it from department name:
  const deptName = p?.department_name || "";
  if (deptName) {
    setText("gs-program", `BACHELOR OF SCIENCE IN ${deptName.toUpperCase()}`);
  } else {
    setText("gs-program", "—");
  }

  // Current semester from CGPA analytics
  const semList = c?.semester_performance || [];
  let currentSem = "—";
  if (semList.length) {
    currentSem = semList[semList.length - 1].semester || "—";
  } else if (p?.semester) {
    currentSem = `Semester ${p.semester}`;
  }
  setText("gs-semester", currentSem.toUpperCase());

  // Stats
  const cgpaVal = c?.cgpa ?? p?.cgpa ?? 0;
  setText("gs-cgpa", Number(cgpaVal).toFixed(2));
  setText("gs-total-courses", String(state.results.length));
  setText("gs-credits", String(c?.total_credits ?? p?.total_credits_completed ?? 0));

  // Best grade
  const grades = state.results.map((r) => r.grade).filter(Boolean);
  const gradeOrder = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "D", "F"];
  const best = gradeOrder.find((g) => grades.includes(g)) || "—";
  setText("gs-best-grade", best);
}

// ─── Semester tabs ─────────────────────────────────────────────────────────────
function buildSemesterTabs() {
  const results = state.results;
  const semSet = new Set(["All"]);
  results.forEach((r) => {
    const lbl = semesterLabel(r);
    if (lbl !== "—") semSet.add(lbl);
  });

  const host = document.getElementById("gs-semester-tabs");
  if (!host) return;

  host.innerHTML = Array.from(semSet)
    .map(
      (s) =>
        `<button class="gs-sem-tab${s === state.filteredSemester ? " active" : ""}" data-sem="${s}">${s}</button>`
    )
    .join("");

  host.querySelectorAll(".gs-sem-tab").forEach((btn) =>
    btn.addEventListener("click", () => {
      state.filteredSemester = btn.dataset.sem;
      host.querySelectorAll(".gs-sem-tab").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      renderTable();
    })
  );
}

// ─── Grade table ───────────────────────────────────────────────────────────────
function renderTable() {
  const tbody = document.getElementById("gs-tbody");
  if (!tbody) return;

  let filtered = state.results;
  if (state.filteredSemester !== "All") {
    filtered = state.results.filter((r) => semesterLabel(r) === state.filteredSemester);
  }

  if (!filtered.length) {
    tbody.innerHTML = `<tr><td colspan="9" class="table-empty">No grades in this semester.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered
    .map((r, i) => {
      const sem = semesterLabel(r);
      const marksText = r.marks || `${r.marks_obtained ?? "—"}/${r.total_marks ?? "—"}`;
      const pct = r.percentage ?? (r.marks_obtained && r.total_marks
        ? Math.round((r.marks_obtained / r.total_marks) * 100)
        : null);
      const pctDisplay = pct !== null ? `${pct}%` : "—";
      const color = pct !== null ? pctColor(pct) : "#94a3b8";
      const gClass = gradeClass(r.grade);
      const gp = r.grade_points != null ? Number(r.grade_points).toFixed(1) : "—";
      const statusBadge =
        r.grade === "F"
          ? `<span class="badge badge-red">Failed</span>`
          : r.grade
          ? `<span class="badge badge-emerald">Passed</span>`
          : `<span class="badge badge-gray">Pending</span>`;

      return `
        <tr>
          <td style="color:var(--text-secondary)">${i + 1}</td>
          <td><span class="badge badge-violet">${dash(r.course)}</span></td>
          <td style="font-weight:500">${dash(r.course_name || r.course)}</td>
          <td><span class="badge badge-blue">${sem}</span></td>
          <td style="font-weight:600">${marksText}</td>
          <td>
            <div class="gs-pct-wrap">
              <span class="gs-pct-text">${pctDisplay}</span>
              ${pct !== null ? `<div class="gs-pct-bar"><div class="gs-pct-fill" style="width:${pct}%;background:${color}"></div></div>` : ""}
            </div>
          </td>
          <td>
            <div class="grade-badge ${gClass}">${dash(r.grade)}</div>
          </td>
          <td style="font-weight:700;color:var(--accent-violet)">${gp}</td>
          <td>${statusBadge}</td>
        </tr>
      `;
    })
    .join("");
}

// ─── Build preview document HTML ──────────────────────────────────────────────
function buildPreviewHTML(filtered) {
  const p = state.profile;
  const me = state.me;
  const c = state.cgpa;
  const fullName = p?.user_name || `${me?.first_name || ""} ${me?.last_name || ""}`.trim() || "—";
  const cgpaVal = c?.cgpa ?? p?.cgpa ?? 0;
  const generatedDate = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const rows = filtered
    .map(
      (r, i) => `
      <tr>
        <td>${i + 1}</td>
        <td>${r.course || "—"}</td>
        <td>${r.course_name || r.course || "—"}</td>
        <td>${semesterLabel(r)}</td>
        <td>${r.marks || `${r.marks_obtained ?? "—"}/${r.total_marks ?? "—"}`}</td>
        <td>${r.percentage != null ? r.percentage + "%" : r.marks_obtained && r.total_marks ? Math.round((r.marks_obtained / r.total_marks) * 100) + "%" : "—"}</td>
        <td style="font-weight:700;color:#7c3aed">${r.grade || "—"}</td>
        <td>${r.grade_points != null ? Number(r.grade_points).toFixed(1) : "—"}</td>
      </tr>`
    )
    .join("");

  return `
  <div class="gs-doc" id="gs-doc-content">
    <div class="gs-doc-header">
      <div class="gs-doc-uni">🎓 Smart University Management System</div>
      <div class="gs-doc-title">Official Grade Sheet</div>
      <div class="gs-doc-subtitle">Generated: ${generatedDate}</div>
    </div>
    <div class="gs-doc-info">
      <div class="gs-doc-info-row">
        <span class="gs-doc-info-label">Student Name</span>
        <span class="gs-doc-info-val">${fullName}</span>
      </div>
      <div class="gs-doc-info-row">
        <span class="gs-doc-info-label">Student ID</span>
        <span class="gs-doc-info-val">${p?.student_id || "—"}</span>
      </div>
      <div class="gs-doc-info-row">
        <span class="gs-doc-info-label">Department</span>
        <span class="gs-doc-info-val">${p?.department_name || "—"}</span>
      </div>
      <div class="gs-doc-info-row">
        <span class="gs-doc-info-label">Program</span>
        <span class="gs-doc-info-val">BSc. in ${p?.department_name || "—"}</span>
      </div>
      <div class="gs-doc-info-row">
        <span class="gs-doc-info-label">Batch</span>
        <span class="gs-doc-info-val">${p?.batch || "—"}</span>
      </div>
      <div class="gs-doc-info-row">
        <span class="gs-doc-info-label">Total Credits</span>
        <span class="gs-doc-info-val">${c?.total_credits ?? p?.total_credits_completed ?? 0}</span>
      </div>
    </div>
    <table class="gs-doc-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Code</th>
          <th>Course Name</th>
          <th>Semester</th>
          <th>Marks</th>
          <th>%</th>
          <th>Grade</th>
          <th>GP</th>
        </tr>
      </thead>
      <tbody>${rows || '<tr><td colspan="8" style="text-align:center;color:#94a3b8;padding:20px;">No grades recorded yet.</td></tr>'}</tbody>
    </table>
    <div class="gs-doc-summary">
      <div>
        <div class="gs-doc-cgpa-label">CUMULATIVE GPA</div>
        <div class="gs-doc-cgpa">${Number(cgpaVal).toFixed(2)} / 4.00</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:0.75rem;color:#64748b">Total Courses Graded</div>
        <div style="font-size:1.25rem;font-weight:700;color:#0f172a">${filtered.length}</div>
      </div>
    </div>
    <div class="gs-doc-footer">
      This document is computer generated and does not require a signature.<br/>
      Smart University Management System — Confidential Academic Record
    </div>
  </div>`;
}

// ─── PDF download via window.print trick (CSS print-optimized) ─────────────────
function downloadAsPDF() {
  // Use browser print-to-PDF with a clean popup
  const filtered = state.filteredSemester === "All"
    ? state.results
    : state.results.filter((r) => semesterLabel(r) === state.filteredSemester);

  const docHTML = buildPreviewHTML(filtered);
  const printWindow = window.open("", "_blank", "width=900,height=700");

  printWindow.document.write(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <title>Grade Sheet</title>
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #fff; color: #1e293b; padding: 32px; }
        .gs-doc { max-width: 800px; margin: 0 auto; }
        .gs-doc-header { text-align: center; border-bottom: 2px solid #7c3aed; padding-bottom: 16px; margin-bottom: 20px; }
        .gs-doc-uni { font-family: 'Outfit', sans-serif; font-size: 1rem; font-weight: 800; color: #0f1629; text-transform: uppercase; letter-spacing: 0.08em; }
        .gs-doc-title { font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 700; color: #7c3aed; margin: 6px 0 2px; }
        .gs-doc-subtitle { font-size: 0.75rem; color: #64748b; }
        .gs-doc-info { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 24px; background: #f8fafc; border-radius: 8px; padding: 16px; margin-bottom: 20px; }
        .gs-doc-info-row { display: flex; gap: 8px; font-size: 0.78rem; }
        .gs-doc-info-label { color: #64748b; font-weight: 500; min-width: 120px; }
        .gs-doc-info-val { font-weight: 600; color: #0f172a; }
        .gs-doc-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; margin-bottom: 20px; }
        .gs-doc-table th { background: #7c3aed; color: #fff; padding: 9px 11px; text-align: left; font-weight: 600; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; }
        .gs-doc-table td { padding: 9px 11px; border-bottom: 1px solid #e2e8f0; color: #1e293b; }
        .gs-doc-table tr:last-child td { border-bottom: none; }
        .gs-doc-table tr:nth-child(even) td { background: #f8fafc; }
        .gs-doc-summary { display: flex; justify-content: space-between; align-items: flex-end; border-top: 2px solid #7c3aed; padding-top: 16px; }
        .gs-doc-cgpa { font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 800; color: #7c3aed; }
        .gs-doc-cgpa-label { font-size: 0.72rem; color: #64748b; }
        .gs-doc-footer { text-align: center; font-size: 0.68rem; color: #94a3b8; margin-top: 16px; padding-top: 16px; border-top: 1px solid #e2e8f0; }
        @media print { @page { margin: 1cm; } }
      </style>
    </head>
    <body>
      ${docHTML}
      <script>
        window.onload = function() {
          setTimeout(() => { window.print(); }, 400);
        };
      <\/script>
    </body>
    </html>
  `);
  printWindow.document.close();
}

// ─── Preview modal ─────────────────────────────────────────────────────────────
function openPreview() {
  const filtered = state.filteredSemester === "All"
    ? state.results
    : state.results.filter((r) => semesterLabel(r) === state.filteredSemester);

  const body = document.getElementById("gs-preview-body");
  if (body) body.innerHTML = buildPreviewHTML(filtered);

  show("gs-preview-overlay");
}

function closePreview() {
  hide("gs-preview-overlay");
}

// ─── Main load ─────────────────────────────────────────────────────────────────
async function main() {
  // Guard: student only
  const role = getRole();
  if (role && role !== "student") {
    window.location.href = role === "teacher" ? "/teacher/dashboard/" : "/admin-panel/dashboard/";
    return;
  }

  show("gs-loading");
  hide("gs-content");

  try {
    await ensureMeLoaded();
    state.me = getUser();

    const [profile, cgpa, resultsData] = await Promise.all([
      api.students.profile(),
      api.students.cgpa(),
      api.exams.myResults(),
    ]);

    state.profile = profile;
    state.cgpa = cgpa;
    state.results = resultsData?.results || [];

    hide("gs-loading");
    show("gs-content");

    if (state.results.length === 0) {
      show("gs-empty");
      hide("gs-table-wrap");
    } else {
      hide("gs-empty");
      show("gs-table-wrap");
    }

    renderInfo();
    buildSemesterTabs();
    renderTable();

  } catch (e) {
    hide("gs-loading");
    show("gs-content");
    toast.error("Load failed", e.message || "Could not load grade sheet data.");
  }

  // Wire up buttons
  document.getElementById("btn-download-pdf")?.addEventListener("click", downloadAsPDF);
  document.getElementById("btn-preview-pdf")?.addEventListener("click", openPreview);
  document.getElementById("gs-preview-close")?.addEventListener("click", closePreview);
  document.getElementById("gs-preview-cancel")?.addEventListener("click", closePreview);
  document.getElementById("gs-preview-download")?.addEventListener("click", () => {
    closePreview();
    downloadAsPDF();
  });

  // Close preview on overlay click
  document.getElementById("gs-preview-overlay")?.addEventListener("click", (e) => {
    if (e.target === document.getElementById("gs-preview-overlay")) closePreview();
  });
}

main();
