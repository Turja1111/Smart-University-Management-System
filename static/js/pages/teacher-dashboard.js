import { api, ensureMeLoaded } from "../api.js";
import { getDisplayName, isVerified } from "../auth.js";
import { toast } from "../toast.js";
import { countUp } from "../utils.js";
import { makeBarChart } from "../charts.js";

let barChart;

async function render() {
  try {
    // Show unverified banner immediately
    const banner = document.getElementById("unverified-banner");
    if (banner && !isVerified()) banner.style.display = "block";

    await ensureMeLoaded();

    const [courses, submissions, notices] = await Promise.all([
      api.teachers.myCourses(),
      api.courses.submissions(),
      api.notices.list(),
    ]);

    const name = getDisplayName().split(" ")[0] || "Teacher";
    const heroTitle = document.getElementById("teacher-hero-title");
    const hour = new Date().getHours();
    const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
    if (heroTitle) heroTitle.textContent = `${greeting}, ${name}! 👨‍🏫`;

    const courseList = courses?.results ?? courses ?? [];
    const submissionList = submissions?.results ?? submissions ?? [];
    const noticeList = notices?.results ?? notices ?? [];

    const totalStudents = courseList.reduce((sum, c) => sum + (c.enrolled_count || 0), 0);
    const pending = submissionList.filter(s => s.marks_obtained === null || s.marks_obtained === undefined).length;
    const thisMonth = new Date().getMonth();
    const noticesThisMonth = noticeList.filter(n => new Date(n.created_at).getMonth() === thisMonth).length;

    const el = (id) => document.getElementById(id);
    const setCount = (id, val) => {
      const e = el(id);
      if (e) { e.dataset.count = val; countUp(e, val, 1000); }
    };

    setCount("t-stat-courses", courseList.length);
    setCount("t-stat-students", totalStudents);
    setCount("t-stat-pending", pending);
    setCount("t-stat-notices", noticesThisMonth);

    // Render course cards
    const grid = document.getElementById("teacher-courses-grid");
    if (grid) {
      if (!courseList.length) {
        grid.innerHTML = `<div class="table-empty" style="grid-column:1/-1;">No courses assigned yet.</div>`;
      } else {
        grid.innerHTML = courseList.map(c => `
          <div class="glass-card" style="padding:0;">
            <div class="glass-card-inner">
              <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
                <div>
                  <div style="font-weight:700; font-size:1rem; color:var(--text-primary)">${c.code || "—"}</div>
                  <div style="font-size:0.85rem; color:var(--text-muted); margin-top:2px;">${c.name || "—"}</div>
                </div>
                <span class="badge badge-blue">${c.enrolled_count || 0} Students</span>
              </div>
              <div style="display:flex; gap:8px; margin-top:12px;">
                <a href="/teacher/attendance/" class="btn btn-sm btn-ghost" style="flex:1; text-align:center;">📅 Attendance</a>
                <a href="/teacher/grades/" class="btn btn-sm btn-ghost" style="flex:1; text-align:center;">📊 Grades</a>
              </div>
            </div>
          </div>
        `).join("");
      }
    }

    // Analytics chart — score distribution for first course
    if (courseList.length) {
      try {
        const analytics = await api.teachers.analytics(courseList[0].id);
        const barCtx = document.getElementById("teacher-bar-chart");
        if (barCtx && analytics) {
          const labels = analytics.score_distribution?.map(d => d.range) || ["0-40", "41-60", "61-80", "81-100"];
          const values = analytics.score_distribution?.map(d => d.count) || [5, 12, 18, 8];
          if (barChart) barChart.destroy();
          barChart = makeBarChart(barCtx, labels, values, "#7C3AED");
        }
      } catch (_) { /* analytics optional */ }
    }

  } catch (e) {
    toast.error("Load failed", "Could not load teacher dashboard.");
    console.error(e);
  }
}

render();
