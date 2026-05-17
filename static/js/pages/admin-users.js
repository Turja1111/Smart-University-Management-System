import { api, ensureMeLoaded } from "../api.js";
import { getRole } from "../auth.js";
import { toast } from "../toast.js";
import { show, hide } from "../modal.js";

let users = [];

function esc(s) {
  if (s == null) return "—";
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
}

async function loadUsers() {
  const tbody = document.getElementById("admin-users-tbody");
  tbody.innerHTML = `<tr><td colspan="5" class="table-empty">Loading users…</td></tr>`;
  try {
    const search = document.getElementById("search-users").value.trim();
    const roleFilt = document.getElementById("filter-role").value;
    
    let url = "/auth/admin/users/?page_size=100";
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (roleFilt) url += `&role=${encodeURIComponent(roleFilt)}`;

    const res = await api.get(url);
    users = res.results || res;

    if (!users.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="table-empty">No users found.</td></tr>`;
      return;
    }

    tbody.innerHTML = users.map(u => {
      const roleBadge = u.role === "admin" ? "badge-red" : u.role === "teacher" ? "badge-blue" : "badge-violet";
      const dt = new Date(u.date_joined).toLocaleDateString();
      return `
        <tr>
          <td>
            <div style="font-weight:600; color:var(--text-primary)">${esc(u.full_name)}</div>
            <div style="font-size:0.75rem; color:var(--text-muted)">@${esc(u.username)}</div>
          </td>
          <td>${esc(u.email)}</td>
          <td><span class="badge ${roleBadge}">${esc(u.role).toUpperCase()}</span></td>
          <td>${dt}</td>
          <td style="text-align: right;">
            <button class="btn btn-sm btn-ghost btn-edit" data-id="${u.id}">✏️ Edit</button>
            <button class="btn btn-sm btn-ghost danger btn-delete" data-id="${u.id}">🗑️</button>
          </td>
        </tr>
      `;
    }).join("");

    document.querySelectorAll(".btn-edit").forEach(b => b.addEventListener("click", (e) => openModal(e.target.dataset.id)));
    document.querySelectorAll(".btn-delete").forEach(b => b.addEventListener("click", (e) => deleteUser(e.target.dataset.id)));

  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="5" class="table-empty">Failed to load users.</td></tr>`;
    toast.error("Error", e.message || "Failed to load users");
  }
}

async function deleteUser(id) {
  if (!confirm("Are you sure you want to completely delete this user? This cannot be undone.")) return;
  try {
    await api.admin.deleteUser(id);
    toast.success("Deleted", "User has been removed.");
    loadUsers();
  } catch (e) {
    toast.error("Error", e.message || "Could not delete user.");
  }
}

function openModal(id = null) {
  const user = id ? users.find(u => String(u.id) === String(id)) : null;
  const isEdit = !!user;

  const body = `
    <div class="form-group">
      <label class="form-label">Email Address</label>
      <input type="email" id="m-email" class="form-control" value="${esc(user?.email || "")}" ${isEdit ? 'readonly style="opacity:0.6"' : ""} />
    </div>
    <div class="form-grid-2 form-group">
      <div>
        <label class="form-label">First Name</label>
        <input type="text" id="m-fn" class="form-control" value="${esc(user?.first_name || "")}" />
      </div>
      <div>
        <label class="form-label">Last Name</label>
        <input type="text" id="m-ln" class="form-control" value="${esc(user?.last_name || "")}" />
      </div>
    </div>
    <div class="form-grid-2 form-group">
      <div>
        <label class="form-label">Role</label>
        <select id="m-role" class="form-control" ${isEdit ? 'disabled' : ''}>
          <option value="student" ${user?.role === 'student' ? 'selected' : ''}>Student</option>
          <option value="teacher" ${user?.role === 'teacher' ? 'selected' : ''}>Teacher</option>
          <option value="admin" ${user?.role === 'admin' ? 'selected' : ''}>Admin</option>
        </select>
      </div>
      <div>
        <label class="form-label">Password ${isEdit ? '(leave blank to keep)' : ''}</label>
        <input type="password" id="m-pw" class="form-control" placeholder="${isEdit ? '***' : 'sums1234'}" />
      </div>
    </div>
  `;

  show({
    title: isEdit ? "Edit User" : "Add New User",
    body,
    footer: `
      <button class="btn btn-secondary" id="m-cancel">Cancel</button>
      <button class="btn btn-primary" id="m-save">Save User</button>
    `
  });

  document.getElementById("m-cancel").addEventListener("click", hide);
  document.getElementById("m-save").addEventListener("click", async () => {
    const payload = {
      first_name: document.getElementById("m-fn").value,
      last_name: document.getElementById("m-ln").value,
    };
    const pw = document.getElementById("m-pw").value;
    if (pw) payload.password = pw;

    try {
      if (isEdit) {
        await api.admin.updateUser(id, payload);
        toast.success("Updated", "User profile saved.");
      } else {
        payload.email = document.getElementById("m-email").value;
        payload.username = payload.email.split("@")[0]; // simple default username
        payload.role = document.getElementById("m-role").value;
        await api.post("/auth/admin/users/", payload);
        toast.success("Created", "New user added.");
      }
      hide();
      loadUsers();
    } catch (e) {
      toast.error("Save Failed", e.message || "Please check the form data.");
    }
  });
}

async function init() {
  const role = getRole();
  if (role !== "admin") {
    window.location.href = "/login/";
    return;
  }
  await ensureMeLoaded();
  
  document.getElementById("search-users").addEventListener("input", () => loadUsers());
  document.getElementById("filter-role").addEventListener("change", () => loadUsers());
  document.getElementById("btn-add-user").addEventListener("click", () => openModal());
  
  loadUsers();
}

init();
