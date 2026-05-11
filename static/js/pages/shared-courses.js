import { api, ensureMeLoaded } from "../api.js";
import { getRole } from "../auth.js";
import { toast } from "../toast.js";

function summarizeSchedule(schedule) {
  const slots = schedule?.slots;
  if (!Array.isArray(slots) || !slots.length) return "—";
  const parts = slots.slice(0, 3).map((s) => {
    const d = (s.weekday || "").slice(0, 3);
    const t = s.start_time || "";
    const k = s.kind ? ` (${s.kind})` : "";
    return `${d} ${t}${k}`;
  });
  const more = slots.length > 3 ? " …" : "";
  return parts.join("; ") + more;
}

// Enroll functionality moved to Advising panel.

async function render() {
  const tbody = document.getElementById("courses-tbody");
  if (!tbody) return;

  try {
    await ensureMeLoaded();
    const data = await api.get("/courses/courses/?page_size=2000");
    const list = data?.results ?? data ?? [];
    const role = getRole();

    if (!list.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="table-empty">No courses available.</td></tr>`;
      return;
    }

    tbody.innerHTML = list
      .map((c) => {
        const teacher = c.teacher_name || c.schedule?.faculty_theory_initial || "—";
        const sched = summarizeSchedule(c.schedule);
        return `<tr>
          <td>${c.code || "—"}</td>
          <td>${c.name || "—"}</td>
          <td>${teacher}</td>
          <td>${c.credits ?? "—"}</td>
          <td class="schedule-cell">${sched}</td>
        </tr>`;
      })
      .join("");


  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="5" class="table-empty">Could not load courses.</td></tr>`;
    toast.error("Load failed", e?.message || "Try logging in again.");
  }
}

render();
