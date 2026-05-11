import { api, ensureMeLoaded } from "../api.js";
import { toast } from "../toast.js";

let availableCourses = [];
let enrolledCourses = []; // [{ enrollmentId, course }]

const WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

function parseTimeMinutes(t) {
  if (!t) return null;
  const m = t.trim().match(/^(\d{1,2}):(\d{2})\s*([AP]M)$/i);
  if (!m) return null;
  let hh = parseInt(m[1], 10);
  const mm = parseInt(m[2], 10);
  const ap = m[3].toUpperCase();
  if (ap === "PM" && hh !== 12) hh += 12;
  if (ap === "AM" && hh === 12) hh = 0;
  return hh * 60 + mm;
}

function intervalsOverlap(smA, emA, smB, emB) {
  return !(emA <= smB || emB <= smA);
}

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

function checkConflict(newCourse) {
  const newSlots = newCourse.schedule?.slots || [];
  
  for (const enr of enrolledCourses) {
    const existingSlots = enr.course.schedule?.slots || [];
    
    for (const ns of newSlots) {
      if (!ns.weekday) continue;
      for (const es of existingSlots) {
        if (!es.weekday || ns.weekday !== es.weekday) continue;
        
        const smA = parseTimeMinutes(ns.start_time);
        let emA = parseTimeMinutes(ns.end_time);
        if (emA == null || emA <= smA) emA = smA + 60;
        
        const smB = parseTimeMinutes(es.start_time);
        let emB = parseTimeMinutes(es.end_time);
        if (emB == null || emB <= smB) emB = smB + 60;
        
        if (smA !== null && smB !== null && intervalsOverlap(smA, emA, smB, emB)) {
          return {
            conflict: true,
            message: `Clash detected on ${ns.weekday}: ${newCourse.code} overlaps with ${enr.course.code}.`
          };
        }
      }
    }
  }
  return { conflict: false };
}

async function enroll(courseId, btn) {
  const course = availableCourses.find(c => c.id === courseId);
  if (!course) return;

  const conflictCheck = checkConflict(course);
  if (conflictCheck.conflict) {
    toast.error("Schedule Conflict", conflictCheck.message);
    return;
  }

  try {
    btn.disabled = true;
    btn.textContent = "Adding...";
    const res = await api.post("/courses/enrollments/", { course: courseId });
    toast.success("Enrolled", `Successfully added ${course.code} to your schedule.`);
    
    // Move from available to enrolled
    enrolledCourses.push({ enrollmentId: res.id, course: course });
    render();
  } catch (e) {
    toast.error("Enrollment failed", e?.data?.error || e.message || "Try again.");
    btn.disabled = false;
    btn.textContent = "Add";
  }
}

async function drop(enrollmentId, courseId) {
  if (!confirm("Are you sure you want to remove this course from your schedule?")) return;
  
  try {
    await api.delete(`/courses/enrollments/${enrollmentId}/`);
    toast.success("Removed", "Course removed from schedule.");
    
    // Find and move to available (if we originally fetched it)
    const enrIdx = enrolledCourses.findIndex(e => e.enrollmentId === enrollmentId);
    if (enrIdx !== -1) {
      enrolledCourses.splice(enrIdx, 1);
    }
    render();
  } catch (e) {
    toast.error("Drop failed", e?.data?.error || e.message || "Try again.");
  }
}

function renderGrid() {
  const tbody = document.getElementById("schedule-grid-tbody");
  if (!enrolledCourses.length) {
    tbody.innerHTML = `<tr><td colspan="8" class="table-empty">No courses selected yet.</td></tr>`;
    return;
  }

  // 1. Extract all unique time slots across all enrolled courses
  const timeSlotsSet = new Set();
  const allSlots = [];
  
  enrolledCourses.forEach(enr => {
    (enr.course.schedule?.slots || []).forEach(slot => {
      if (!slot.weekday || !slot.start_time) return;
      const tStart = slot.start_time;
      const tEnd = slot.end_time || tStart;
      const label = `${tStart} - ${tEnd}`;
      
      const sm = parseTimeMinutes(tStart);
      
      timeSlotsSet.add(JSON.stringify({ label, sm, start: tStart, end: tEnd }));
      allSlots.push({ ...slot, course: enr.course, enrollmentId: enr.enrollmentId });
    });
  });

  const uniqueTimes = Array.from(timeSlotsSet)
    .map(s => JSON.parse(s))
    .sort((a, b) => a.sm - b.sm);

  if (!uniqueTimes.length) {
    tbody.innerHTML = `<tr><td colspan="8" class="table-empty">Courses have no specific time slots.</td></tr>`;
    return;
  }

  let html = "";
  uniqueTimes.forEach(timeObj => {
    html += `<tr>`;
    html += `<td class="time-cell">${timeObj.label}</td>`;
    
    WEEKDAYS.forEach(day => {
      // Find slots that match this day and time
      const matchingSlots = allSlots.filter(s => 
        s.weekday.toLowerCase() === day.toLowerCase() && 
        s.start_time === timeObj.start &&
        (s.end_time || s.start_time) === timeObj.end
      );
      
      if (matchingSlots.length > 0) {
        html += `<td>`;
        matchingSlots.forEach(ms => {
          const isLab = ms.kind === 'lab' || ms.kind === 'Lab';
          const pillClass = isLab ? 'course-pill lab' : 'course-pill';
          const roomStr = ms.room && ms.room !== '—' ? ` - ${ms.room}` : '';
          
          html += `<div class="${pillClass}" title="${ms.course.name}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              <span><strong>${ms.course.code}</strong>${roomStr}</span>
              <button class="btn btn-ghost btn-sm p-0" style="color:inherit; opacity:0.7; transform:scale(0.8);" title="Remove" data-drop="${ms.enrollmentId}" data-course="${ms.course.id}">❌</button>
            </div>
            <div style="font-size:0.75rem; margin-top:4px; opacity:0.9;">${ms.kind || 'Class'}</div>
          </div>`;
        });
        html += `</td>`;
      } else {
        html += `<td></td>`;
      }
    });
    
    html += `</tr>`;
  });

  tbody.innerHTML = html;

  // Add event listeners for drop buttons inside grid
  tbody.querySelectorAll("[data-drop]").forEach(btn => {
    btn.addEventListener("click", () => drop(parseInt(btn.dataset.drop, 10), parseInt(btn.dataset.course, 10)));
  });
}

function renderAvailable() {
  const tbody = document.getElementById("available-courses-tbody");
  
  // Filter out already enrolled courses
  const enrolledIds = new Set(enrolledCourses.map(e => e.course.id));
  const toShow = availableCourses.filter(c => !enrolledIds.has(c.id));

  if (!toShow.length) {
    tbody.innerHTML = `<tr><td colspan="5" class="table-empty">No more courses available.</td></tr>`;
    return;
  }

  tbody.innerHTML = toShow
    .map(c => {
      const sched = summarizeSchedule(c.schedule);
      return `<tr>
        <td><strong>${c.code || "—"}</strong></td>
        <td>${c.name || "—"}</td>
        <td>${c.credits ?? "—"}</td>
        <td class="schedule-cell" style="font-size: 0.85rem;">${sched}</td>
        <td>
          <button type="button" class="btn btn-primary btn-sm btn-full" data-enroll="${c.id}">Add</button>
        </td>
      </tr>`;
    })
    .join("");

  tbody.querySelectorAll("[data-enroll]").forEach((btn) => {
    btn.addEventListener("click", () => enroll(parseInt(btn.dataset.enroll, 10), btn));
  });
}

function render() {
  renderAvailable();
  renderGrid();
}

async function init() {
  try {
    await ensureMeLoaded();
    
    // Fetch user's current enrollments
    const enrollmentsData = await api.get("/courses/enrollments/");
    const enrollmentsList = enrollmentsData?.results ?? enrollmentsData ?? [];
    
    // Filter out dropped enrollments and store
    enrolledCourses = enrollmentsList
      .filter(e => e.status === 'enrolled')
      .map(e => ({ enrollmentId: e.id, course: e.course }));

    // Fetch all courses
    const data = await api.get("/courses/courses/?page_size=2000");
    availableCourses = data?.results ?? data ?? [];
    
    render();
  } catch (e) {
    console.error("Failed to load advising data", e);
    toast.error("Load failed", e?.message || "Could not load courses.");
  }
}

// Bind methods for global access if needed, else they are local
window.enroll = enroll;
window.drop = drop;

init();
