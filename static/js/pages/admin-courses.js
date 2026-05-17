import { api, ensureMeLoaded } from "../api.js";
import { getRole } from "../auth.js";
import { toast } from "../toast.js";
import { show, hide } from "../modal.js";

let courses = [];
let departments = [];
let teachers = [];

function esc(s) {
  if (s == null) return "—";
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
}

async function loadDependencies() {
  try {
    const depsRes = await api.courses.departments();
    departments = depsRes.results || depsRes || [];
    
    // Quick hack to get users who are teachers
    const tRes = await api.get("/auth/admin/users/?role=teacher&page_size=500");
    teachers = tRes.results || tRes || [];
  } catch (e) {
    console.error("Failed to load departments/teachers", e);
  }
}

async function loadCourses() {
  const tbody = document.getElementById("admin-courses-tbody");
  tbody.innerHTML = `<tr><td colspan="6" class="table-empty">Loading courses…</td></tr>`;
  try {
    const search = document.getElementById("search-courses").value.trim();
    let qs = "?page_size=200";
    if (search) qs += `&search=${encodeURIComponent(search)}`;

    const res = await api.courses.list(qs);
    courses = res.results || res;

    if (!courses.length) {
      tbody.innerHTML = `<tr><td colspan="6" class="table-empty">No courses found.</td></tr>`;
      return;
    }

    tbody.innerHTML = courses.map(c => {
      const activeBadge = c.is_active ? "badge-emerald" : "badge-red";
      const activeText = c.is_active ? "Active" : "Inactive";
      const teacherName = teachers.find(t => t.id === c.teacher)?.full_name || "Unassigned";

      return `
        <tr>
          <td style="font-weight:600; color:var(--text-primary)">${esc(c.code)}</td>
          <td>
            <div style="font-weight:500;">${esc(c.name)}</div>
            <div style="font-size:0.75rem; color:var(--text-muted)">Teacher: ${esc(teacherName)}</div>
          </td>
          <td>${esc(c.department_name)}</td>
          <td>${esc(c.credits)}</td>
          <td><span class="badge ${activeBadge}">${activeText}</span></td>
          <td style="text-align: right;">
            <button class="btn btn-sm btn-ghost btn-edit" data-id="${c.id}">✏️ Edit</button>
            <button class="btn btn-sm btn-ghost danger btn-delete" data-id="${c.id}">🗑️</button>
          </td>
        </tr>
      `;
    }).join("");

    document.querySelectorAll(".btn-edit").forEach(b => b.addEventListener("click", (e) => openModal(e.target.dataset.id)));
    document.querySelectorAll(".btn-delete").forEach(b => b.addEventListener("click", (e) => deleteCourse(e.target.dataset.id)));

  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="6" class="table-empty">Failed to load courses.</td></tr>`;
    toast.error("Error", e.message || "Failed to load courses");
  }
}

async function deleteCourse(id) {
  if (!confirm("Are you sure you want to completely delete this course? This will remove all enrollments and grades associated with it!")) return;
  try {
    await api.courses.delete(id);
    toast.success("Deleted", "Course has been removed.");
    loadCourses();
  } catch (e) {
    toast.error("Error", e.message || "Could not delete course.");
  }
}

function openModal(id = null) {
  const course = id ? courses.find(c => String(c.id) === String(id)) : null;
  const isEdit = !!course;

  const depOptions = departments.map(d => `<option value="${d.id}" ${course?.department === d.id ? 'selected' : ''}>${esc(d.name)}</option>`).join("");
  const tOptions = teachers.map(t => `<option value="${t.id}" ${course?.teacher === t.id ? 'selected' : ''}>${esc(t.full_name)}</option>`).join("");

  const body = `
    <div class="form-grid-2 form-group">
      <div>
        <label class="form-label">Course Code</label>
        <input type="text" id="m-code" class="form-control" value="${esc(course?.code || "")}" placeholder="e.g. CS101" />
      </div>
      <div>
        <label class="form-label">Course Name</label>
        <input type="text" id="m-name" class="form-control" value="${esc(course?.name || "")}" placeholder="Introduction to CS" />
      </div>
    </div>
    <div class="form-grid-2 form-group">
      <div>
        <label class="form-label">Department</label>
        <select id="m-dep" class="form-control">
          <option value="">Select Department</option>
          ${depOptions}
        </select>
      </div>
      <div>
        <label class="form-label">Credits</label>
        <input type="number" step="0.5" id="m-credits" class="form-control" value="${course?.credits || "3.0"}" />
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Assigned Teacher</label>
      <select id="m-teacher" class="form-control">
        <option value="">Unassigned</option>
        ${tOptions}
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">Description</label>
      <textarea id="m-desc" class="form-control" rows="3">${esc(course?.description || "")}</textarea>
    </div>
    <div class="form-group flex gap-2" style="align-items:center;">
      <input type="checkbox" id="m-active" ${!course || course?.is_active ? 'checked' : ''} />
      <label for="m-active" class="form-label" style="margin:0;">Course is Active</label>
    </div>
  `;

  show({
    title: isEdit ? "Edit Course" : "Add New Course",
    body,
    footer: `
      <button class="btn btn-secondary" id="m-cancel">Cancel</button>
      <button class="btn btn-primary" id="m-save">Save Course</button>
    `
  });

  document.getElementById("m-cancel").addEventListener("click", hide);
  document.getElementById("m-save").addEventListener("click", async () => {
    const payload = {
      code: document.getElementById("m-code").value,
      name: document.getElementById("m-name").value,
      department: document.getElementById("m-dep").value,
      credits: document.getElementById("m-credits").value,
      description: document.getElementById("m-desc").value,
      is_active: document.getElementById("m-active").checked,
    };
    
    const tid = document.getElementById("m-teacher").value;
    if (tid) payload.teacher = tid;

    if (!payload.code || !payload.name || !payload.department) {
      toast.error("Validation", "Code, Name, and Department are required.");
      return;
    }

    try {
      if (isEdit) {
        await api.courses.update(id, payload);
        toast.success("Updated", "Course saved.");
      } else {
        await api.courses.create(payload);
        toast.success("Created", "New course added.");
      }
      hide();
      loadCourses();
    } catch (e) {
      toast.error("Save Failed", e.message || "Please check the form data.");
    }
  });
}

async function init() {
  try { await ensureMeLoaded(); } catch (_) {}
  const role = getRole();
  if (role !== "admin") {
    window.location.href = "/login/";
    return;
  }
  
  document.getElementById("search-courses").addEventListener("input", () => loadCourses());
  document.getElementById("btn-add-course").addEventListener("click", () => openModal());
  
  await loadDependencies();
  loadCourses();
}

init();
