import { api, ensureMeLoaded } from "../api.js";
import { toast } from "../toast.js";

function fmtDate(dt) {
  if (!dt) return "—";
  try {
    return new Date(dt).toLocaleString();
  } catch {
    return dt;
  }
}

async function loadEnrollments() {
  try {
    await ensureMeLoaded();
    const res = await api.courses.myEnrollments();
    const list = res.results || res || [];
    const tbody = document.getElementById("enrolled-courses-tbody");
    if (!tbody) return;
    if (!list.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="table-empty">You are not enrolled in any courses.</td></tr>`;
      return;
    }
    tbody.innerHTML = list
      .map(
        (e) => `
      <tr data-id="${e.id}">
        <td>${e.course_code || "—"}</td>
        <td>${e.course_name || "—"}</td>
        <td>${e.status}</td>
        <td>${fmtDate(e.enrolled_at)}</td>
        <td><button class="btn btn-ghost btn-sm drop-btn" data-id="${e.id}">Drop</button></td>
      </tr>`
      )
      .join("");
    tbody.querySelectorAll(".drop-btn").forEach((b) => b.addEventListener("click", onDrop));
  } catch (err) {
    toast.error("Load failed", err?.data?.detail || err.message || "Could not load enrollments");
  }
}

async function onDrop(ev) {
  const id = ev.currentTarget.dataset.id;
  if (!confirm("Are you sure you want to drop this course?")) return;
  try {
    await api.courses.dropEnrollment(id);
    toast.success("Dropped", "Course dropped successfully.");
    loadEnrollments();
  } catch (err) {
    toast.error("Drop failed", err?.data?.error || err?.data?.detail || err.message || "Could not drop course");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadEnrollments();
});
