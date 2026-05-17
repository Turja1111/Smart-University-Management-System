import { api, ensureMeLoaded } from "../api.js";
import { getDisplayName, isVerified } from "../auth.js";
import { toast } from "../toast.js";
import { countUp } from "../utils.js";
import { makeDoughnutChart, makeLineChart } from "../charts.js";

let cgpaChart;
let gradeChart;

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function initRoutineTabs(days) {
  const tabHost = document.getElementById("routine-tabs");
  const content = document.getElementById("routine-content");
  if (!tabHost || !content) return;

  const names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  tabHost.innerHTML = names
    .map((d, idx) => `<button class="day-tab${idx === 0 ? " active" : ""}" type="button" data-day="${d}">${d.slice(0, 3)}</button>`)
    .join("");

  function renderDay(day) {
    const sched = days?.[day] || [];
    if (!sched.length) {
      content.innerHTML = `<div class="table-empty">No classes on ${day}.</div>`;
      return;
    }
    content.innerHTML = sched
      .map(
        (c) => `
        <div class="glass-card mb-4">
          <div class="glass-card-inner">
            <div class="course-code">${c.course_code || c.course || ""}</div>
            <div class="course-name">${c.course_name || ""}</div>
            <div class="attendance-subrow">
              <span class="badge badge-blue">${c.start_time || "—"} – ${c.end_time || "—"}</span>
              <span class="badge badge-violet">Room ${c.room || "—"}</span>
              ${c.kind ? `<span class="badge badge-amber">${c.kind}</span>` : ""}
            </div>
          </div>
        </div>
      `
      )
      .join("");
  }

  renderDay("Monday");
  tabHost.querySelectorAll(".day-tab").forEach((b) =>
    b.addEventListener("click", () => {
      tabHost.querySelectorAll(".day-tab").forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      renderDay(b.dataset.day);
    })
  );
}

function animateCounts() {
  document.querySelectorAll("[data-count]").forEach((el) => {
    const target = parseFloat(el.dataset.count) || 0;
    const decimals = parseInt(el.dataset.decimal || "0", 10);
    const suffix = el.textContent.includes("%") ? "%" : "";
    countUp(el, target, 1200, decimals, suffix);
  });
}

async function render() {
  try {
    // Show unverified banner immediately (before API calls)
    const banner = document.getElementById("unverified-banner");
    if (banner && !isVerified()) banner.style.display = "block";

    await ensureMeLoaded();
    const [profile, cgpa, routineRes, assignments, attendance] = await Promise.all([
      api.students.profile(),
      api.students.cgpa(),
      api.students.routine(),
      api.courses.assignments(),
      api.attendance.myAttendance(),
    ]);

    const name = getDisplayName().split(" ")[0] || "Student";
    setText("hero-title", `Welcome back, ${name}! 🎓`);

    const attList = attendance?.results || attendance || [];
    const avgAtt = attList.length ? Math.round(attList.reduce((s, r) => s + (r.percentage || 0), 0) / attList.length) : 0;

    const cgpaVal = cgpa?.cgpa ?? cgpa?.current_cgpa ?? 0;
    setText("hero-cgpa", Number(cgpaVal).toFixed(2));
    setText("hero-att", `${avgAtt}%`);
    setText("hero-courses", `${attList.length}`);

    setText("stat-cgpa", Number(cgpaVal).toFixed(2));
    setText("stat-att", `${avgAtt}%`);
    setText("stat-att-sub", avgAtt >= 75 ? "✅ Good standing" : "⚠️ Needs improvement");
    setText("stat-enrolled", `${attList.length}`);

    const asgs = assignments?.results || assignments || [];
    const pending = asgs.filter((a) => !a.is_submitted).length;
    setText("stat-pending", `${pending}`);

    const tbody = document.getElementById("assignments-tbody");
    if (tbody) {
      const rows = asgs.slice(0, 6).map((a) => {
        const due = a.due_date ? new Date(a.due_date) : null;
        const late = due ? due < new Date() : false;
        const status = a.is_submitted ? "submitted" : late ? "late" : "pending";
        const badge = status === "submitted" ? "badge-emerald" : status === "late" ? "badge-red" : "badge-amber";
        return `<tr><td>${a.course_code || a.course || "—"}</td><td>${a.title || "—"}</td><td>${due ? due.toLocaleDateString() : "—"}</td><td><span class="badge ${badge}">${status}</span></td></tr>`;
      });
      tbody.innerHTML = rows.length ? rows.join("") : `<tr><td colspan="4" class="table-empty">No assignments found</td></tr>`;
    }

    initRoutineTabs(routineRes?.by_day || {});

    const cgpaCtx = document.getElementById("cgpa-chart");
    if (cgpaCtx) {
      if (cgpaChart) cgpaChart.destroy();
      const labels = cgpa?.semesters || ["S1", "S2", "S3", "S4", "S5", "S6"];
      const values = cgpa?.values || [3.2, 3.4, 3.5, 3.7, 3.6, Number(cgpaVal) || 3.8];
      cgpaChart = makeLineChart(cgpaCtx, labels, values, "#7C3AED");
    }

    const gradeCtx = document.getElementById("grade-chart");
    if (gradeCtx) {
      if (gradeChart) gradeChart.destroy();
      gradeChart = makeDoughnutChart(
        gradeCtx,
        ["A+", "A", "B", "C", "D", "F"],
        [15, 25, 30, 20, 7, 3],
        ["#7C3AED", "#3B82F6", "#10B981", "#F59E0B", "#EC4899", "#EF4444"]
      );
    }

    animateCounts();
  } catch (e) {
    toast.error("Load failed", "Could not load dashboard data.");
  }
}

render();

