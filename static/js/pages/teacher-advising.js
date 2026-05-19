import { api, ensureMeLoaded } from "../api.js";
import { toast } from "../toast.js";

let advisings = [];

function render() {
  const tbody = document.getElementById('advising-tbody');
  if (!advisings.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="table-empty">No pending advisings found.</td></tr>';
    return;
  }
  tbody.innerHTML = advisings.map(a => {
    const courses = (a.courses_snapshot || []).join(', ');
    const status = a.student_confirmed ? (a.teacher_approved ? 'Approved' : 'Pending approval') : 'Not confirmed';
    const schedBtn = `<button class="btn btn-ghost btn-sm" onclick="viewSchedule(${a.student})">Schedule</button>`;
    return `<tr>
      <td>${a.student_name}</td>
      <td>${a.semester}</td>
      <td>${a.year}</td>
      <td>${courses || '—'}</td>
      <td>${status}</td>
      <td><div style="display:flex; gap:8px;">${schedBtn}${btn}</div></td>
    </tr>`;
  }).join('');

  tbody.querySelectorAll('[data-approve]').forEach(b => {
    b.addEventListener('click', async () => {
      const id = b.dataset.approve;
      if (!confirm('Approve this student advising and snapshot their courses?')) return;
      try {
        const res = await api.post(`/courses/advisings/${id}/approve/`);
        toast.success('Approved', `Advising for ${res.student_name} approved.`);
        // remove from list
        advisings = advisings.filter(x => x.id !== res.id);
        render();
      } catch (e) {
        toast.error('Approve failed', e?.data?.error || e?.message || 'Try again.');
      }
    });
  });
}

async function init() {
  try {
    await ensureMeLoaded();
    // fetch all advisings and filter
    const data = await api.get('/courses/advisings/?page_size=2000');
    const items = data?.results ?? data ?? [];
    advisings = items.filter(a => a.student_confirmed && !a.teacher_approved);
    render();
  } catch (e) {
    console.error('Failed to load advisings', e);
    const tbody = document.getElementById('advising-tbody');
    if (tbody) tbody.innerHTML = '<tr><td colspan="6" class="table-empty">Failed to load advisings.</td></tr>';
  }
}

}

window.viewSchedule = async (studentId) => {
  const modal = document.getElementById("schedule-modal");
  const content = document.getElementById("schedule-modal-content");
  if (!modal || !content) return;
  modal.style.display = "flex";
  content.innerHTML = "Loading...";

  try {
    const res = await api.get(`/students/my-routine/?student_id=${studentId}`);
    const days = res.by_day || {};
    let html = "";
    const names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    for (const d of names) {
      if (days[d] && days[d].length > 0) {
        html += `<div style="font-weight:600; margin-top:16px; margin-bottom:8px;">${d}</div>`;
        for (const c of days[d]) {
          html += `
            <div style="background:var(--bg-secondary); padding:12px; border-radius:8px; margin-bottom:8px; display:flex; justify-content:space-between;">
              <div>
                <div style="font-weight:600; font-size:0.9rem;">${c.course_code || ""}</div>
                <div style="font-size:0.8rem; color:var(--text-muted);">${c.course_name || ""}</div>
              </div>
              <div style="text-align:right;">
                <span class="badge badge-blue">${c.start_time || "—"} - ${c.end_time || "—"}</span>
              </div>
            </div>`;
        }
      }
    }
    content.innerHTML = html || "<div>No classes scheduled.</div>";
  } catch (e) {
    content.innerHTML = `<div class="table-empty" style="color:red;">Failed to load schedule.</div>`;
  }
};

document.getElementById("close-modal-btn")?.addEventListener("click", () => {
  const modal = document.getElementById("schedule-modal");
  if (modal) modal.style.display = "none";
});

init();
