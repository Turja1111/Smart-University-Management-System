import { api } from "../api.js";
import { toast } from "../toast.js";

function metaFor(pct) {
  if (pct >= 75) return { wrap: "att-emerald", badge: "badge-emerald", label: "Good Standing", fill: "emerald" };
  if (pct >= 60) return { wrap: "att-amber", badge: "badge-amber", label: "At Risk", fill: "amber" };
  return { wrap: "att-red", badge: "badge-red", label: "Critical", fill: "red" };
}

async function render() {
  try {
    const records = await api.attendance.myAttendance();
    const list = records?.results || records || [];

    const avg = list.length ? Math.round(list.reduce((s, r) => s + (r.percentage || 0), 0) / list.length) : 0;
    document.getElementById("att-avg").textContent = `${avg}%`;
    document.getElementById("att-courses").textContent = `${list.length}`;
    document.getElementById("att-good").textContent = `${list.filter((r) => (r.percentage || 0) >= 75).length}`;
    document.getElementById("att-subtitle").textContent = `${list.length} courses enrolled`;

    const warn = document.getElementById("att-warning");
    if (avg < 75) {
      warn.classList.remove("hidden");
      document.getElementById("att-warning-text").textContent = `Your average attendance is ${avg}%. You need at least 75% to be eligible for exams.`;
    } else {
      warn.classList.add("hidden");
    }

    const host = document.getElementById("attendance-list");
    if (!host) return;
    if (!list.length) {
      host.innerHTML = `<div class="table-empty">No attendance records yet.</div>`;
      return;
    }

    host.innerHTML = list
      .map((r, idx) => {
        const pct = Math.round(r.percentage || 0);
        const m = metaFor(pct);
        return `
          <div class="glass-card ${m.wrap}">
            <div class="glass-card-inner">
              <div class="attendance-row">
                <div class="attendance-ring-wrap">
                  <div class="attendance-ring">
                    <svg width="80" height="80" viewBox="0 0 80 80" aria-hidden="true">
                      <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8"></circle>
                      <circle cx="40" cy="40" r="34" fill="none"
                        stroke-width="8"
                        stroke-dasharray="213.62830044410595"
                        stroke-dashoffset="213.62830044410595"
                        class="att-ring-progress"
                        id="att-ring-${idx}"
                      ></circle>
                    </svg>
                    <div class="ring-text">${pct}%</div>
                  </div>
                </div>
                <div class="attendance-meta">
                  <div class="course-code">${r.course_code || r.course || "—"}</div>
                  <div class="course-name">${r.course_name || ""}</div>
                  <div class="attendance-subrow">
                    <span class="badge ${m.badge}">${m.label}</span>
                    <span class="attendance-counts">${r.present || 0} present · ${r.absent || 0} absent · ${r.total || 0} total</span>
                  </div>
                  <div class="mt-4">
                    <progress class="att-progress ${m.fill}" max="100" value="${pct}"></progress>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `;
      })
      .join("");

    // Set ring dashoffsets without inline styles
    const circ = 2 * Math.PI * 34;
    list.forEach((r, idx) => {
      const pct = Math.round(r.percentage || 0);
      const el = document.getElementById(`att-ring-${idx}`);
      if (!el) return;
      const dash = circ - (circ * pct) / 100;
      el.setAttribute("stroke-dasharray", `${circ}`);
      el.setAttribute("stroke-dashoffset", `${dash}`);
    });
  } catch {
    toast.error("Load failed", "Could not load attendance data.");
  }
}

render();

