import { api, ensureMeLoaded } from "../api.js";
import { getRole, getUser, setUser } from "../auth.js";
import { show, hide } from "../modal.js";
import { toast } from "../toast.js";

function escAttr(s) {
  if (!s) return "";
  return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
}

function escTextarea(s) {
  if (!s) return "";
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
}

function dash(v) {
  if (v === null || v === undefined || v === "") return "—";
  return String(v);
}

function formatDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return dash(iso);
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function currentSemesterFromRoutine(routine) {
  const order = { spring: 1, summer: 2, fall: 3 };
  let best = null;
  for (const r of routine || []) {
    const y = Number(r.year) || 0;
    const s = (r.semester || "fall").toLowerCase();
    const score = y * 10 + (order[s] || 0);
    if (!best || score >= best.score) best = { score, y, semester: s };
  }
  if (!best) return "—";
  return `${best.semester.toUpperCase()} ${best.y}`;
}

let state = { profile: null, cgpa: null, routine: null, me: null };

function applyPhoto() {
  const me = state.me || getUser();
  const img = document.getElementById("profile-photo");
  const ph = document.getElementById("profile-photo-ph");
  const url = me?.profile_picture;
  if (url) {
    const full =
      url.startsWith("http") ? url : url.startsWith("/") ? `${window.location.origin}${url}` : url;
    img.src = full;
    img.classList.remove("hidden");
    img.onload = () => ph.classList.add("hidden");
    img.onerror = () => {
      img.classList.add("hidden");
      ph.classList.remove("hidden");
    };
  } else {
    img.classList.add("hidden");
    ph.classList.remove("hidden");
    ph.textContent = (me?.first_name?.[0] || me?.email?.[0] || "?").toUpperCase();
  }
}

function render() {
  const p = state.profile;
  const c = state.cgpa;
  const r = state.routine?.routine || [];
  const me = state.me || getUser();

  if (!p) return;

  document.getElementById("profile-display-name").textContent = p.user_name || dash(me?.full_name);
  document.querySelector("#meta-student-id span").textContent = p.student_id;
  document.querySelector("#meta-department span").textContent = p.department_name || "—";
  const admission = p.admission_session || (p.batch ? `Session ${p.batch}` : "—");
  document.querySelector("#meta-admission span").textContent = admission;

  const credits = c?.total_credits ?? p.total_credits_completed ?? 0;
  document.getElementById("stat-credits").textContent = String(credits);
  const cgpaVal = typeof c?.cgpa === "number" ? c.cgpa : p.cgpa ?? 0;
  document.getElementById("stat-cgpa").textContent = Number(cgpaVal).toFixed(2);
  document.getElementById("stat-current-sem").textContent = currentSemesterFromRoutine(r);

  document.getElementById("ov-full-name").textContent = p.user_name || "—";
  document.getElementById("ov-phone").textContent = dash(p.user_phone);
  document.getElementById("ov-email").textContent = dash(p.user_email);
  document.getElementById("ov-dob").textContent = formatDate(p.date_of_birth);
  document.getElementById("ov-em-name").textContent = dash(p.emergency_contact_name);
  document.getElementById("ov-em-phone").textContent = dash(p.emergency_contact);
  document.getElementById("ov-bc").textContent = dash(p.birth_certificate_no);
  document.getElementById("ov-passport").textContent = dash(p.passport_no);

  document.getElementById("misc-address").textContent = dash(p.address);
  document.getElementById("misc-admission").textContent = dash(p.admission_session);
  document.getElementById("misc-batch").textContent = dash(p.batch);
  document.getElementById("misc-em-name").textContent = dash(p.emergency_contact_name);
  document.getElementById("misc-em-phone").textContent = dash(p.emergency_contact);
  document.getElementById("misc-bc").textContent = dash(p.birth_certificate_no);
  document.getElementById("misc-passport").textContent = dash(p.passport_no);

  document.getElementById("ac-student-id").textContent = p.student_id;
  document.getElementById("ac-dept").textContent = p.department_name || "—";
  document.getElementById("ac-semester").textContent = String(p.semester ?? "—");
  document.getElementById("ac-cgpa-record").textContent = Number(p.cgpa ?? 0).toFixed(2);
  document.getElementById("ac-credits").textContent = String(p.total_credits_completed ?? 0);

  const perf = (c?.semester_performance || [])
    .map((x) => `${x.semester}: GPA ${x.gpa} (${x.credits} cr)`)
    .join("\n");
  document.getElementById("ac-perf").textContent = perf || "—";

  applyPhoto();
}

function openEmailModal() {
  const me = state.me || getUser();
  show({
    title: "Update email",
    body: `
      <label class="profile-modal-label">Email</label>
      <input type="email" class="profile-modal-input" id="modal-email" value="${escAttr(me?.email)}" />
    `,
    footer: `
      <button type="button" class="btn btn-secondary" id="m-email-cancel">Cancel</button>
      <button type="button" class="btn btn-primary" id="m-email-save">Save</button>
    `,
  });
  document.getElementById("m-email-cancel")?.addEventListener("click", hide);
  document.getElementById("m-email-save")?.addEventListener("click", async () => {
    const email = document.getElementById("modal-email")?.value?.trim();
    if (!email) {
      toast.error("Missing email", "Enter a valid email address.");
      return;
    }
    try {
      const updated = await api.auth.updateMe({ email });
      setUser(updated);
      state.me = updated;
      hide();
      await reload();
      toast.success("Email updated", "Your sign-in email has been changed.");
    } catch (e) {
      toast.error("Update failed", e.message || "Try again.");
    }
  });
}

function editFormFields() {
  const p = state.profile;
  const me = state.me || getUser();
  return `
    <div class="profile-modal-grid">
      <div>
        <label class="profile-modal-label">First name</label>
        <input class="profile-modal-input" id="ef-fn" value="${escAttr(me?.first_name)}" />
      </div>
      <div>
        <label class="profile-modal-label">Last name</label>
        <input class="profile-modal-input" id="ef-ln" value="${escAttr(me?.last_name)}" />
      </div>
      <div>
        <label class="profile-modal-label">Mobile no</label>
        <input class="profile-modal-input" id="ef-phone" value="${escAttr(me?.phone)}" />
      </div>
      <div>
        <label class="profile-modal-label">Date of birth</label>
        <input type="date" class="profile-modal-input" id="ef-dob" value="${escAttr(p.date_of_birth)}" />
      </div>
      <div>
        <label class="profile-modal-label">Semester (number)</label>
        <input type="number" min="1" max="20" class="profile-modal-input" id="ef-sem" value="${p.semester ?? 1}" />
      </div>
      <div>
        <label class="profile-modal-label">Batch</label>
        <input class="profile-modal-input" id="ef-batch" value="${escAttr(p.batch)}" />
      </div>
      <div class="profile-modal-span2">
        <label class="profile-modal-label">Address</label>
        <textarea class="profile-modal-input" id="ef-addr" rows="2">${escTextarea(p.address)}</textarea>
      </div>
      <div>
        <label class="profile-modal-label">Admission session</label>
        <input class="profile-modal-input" id="ef-adm" placeholder="SPRING 2022" value="${escAttr(p.admission_session)}" />
      </div>
      <div>
        <label class="profile-modal-label">Emergency contact name</label>
        <input class="profile-modal-input" id="ef-emn" value="${escAttr(p.emergency_contact_name)}" />
      </div>
      <div>
        <label class="profile-modal-label">Emergency contact no.</label>
        <input class="profile-modal-input" id="ef-emp" value="${escAttr(p.emergency_contact)}" />
      </div>
      <div>
        <label class="profile-modal-label">Birth certificate no</label>
        <input class="profile-modal-input" id="ef-bc" value="${escAttr(p.birth_certificate_no)}" />
      </div>
      <div>
        <label class="profile-modal-label">Passport no</label>
        <input class="profile-modal-input" id="ef-pp" value="${escAttr(p.passport_no)}" />
      </div>
    </div>
  `;
}

async function saveEditForm() {
  const p = state.profile;
  const userPayload = {
    first_name: document.getElementById("ef-fn")?.value?.trim(),
    last_name: document.getElementById("ef-ln")?.value?.trim(),
    phone: document.getElementById("ef-phone")?.value?.trim() || "",
  };
  const dobRaw = document.getElementById("ef-dob")?.value?.trim();
  const profPayload = {
    semester: Number(document.getElementById("ef-sem")?.value) || p.semester,
    batch: document.getElementById("ef-batch")?.value?.trim() || "",
    date_of_birth: dobRaw || null,
    address: document.getElementById("ef-addr")?.value?.trim() || "",
    admission_session: document.getElementById("ef-adm")?.value?.trim() || "",
    emergency_contact_name: document.getElementById("ef-emn")?.value?.trim() || "",
    emergency_contact: document.getElementById("ef-emp")?.value?.trim() || "",
    birth_certificate_no: document.getElementById("ef-bc")?.value?.trim() || "",
    passport_no: document.getElementById("ef-pp")?.value?.trim() || "",
  };
  try {
    const [meUp, profUp] = await Promise.all([
      api.auth.updateMe(userPayload),
      api.students.updateProfile(profPayload),
    ]);
    setUser(meUp);
    state.me = meUp;
    state.profile = profUp;
    hide();
    await reload();
    toast.success("Profile saved", "Your information was updated.");
  } catch (e) {
    toast.error("Save failed", e.message || "Check your inputs and try again.");
  }
}

function openEditModal() {
  show({
    title: "Edit profile",
    body: editFormFields(),
    footer: `
      <button type="button" class="btn btn-secondary" id="m-ed-cancel">Cancel</button>
      <button type="button" class="btn btn-primary" id="m-ed-save">Save</button>
    `,
  });
  document.getElementById("m-ed-cancel")?.addEventListener("click", hide);
  document.getElementById("m-ed-save")?.addEventListener("click", saveEditForm);
}

async function reload() {
  const [profile, cgpa, routine] = await Promise.all([
    api.students.profile(),
    api.students.cgpa(),
    api.students.routine(),
  ]);
  state.profile = profile;
  state.cgpa = cgpa;
  state.routine = routine;
  state.me = getUser();
  render();
}

function initTabs() {
  const tabs = document.querySelectorAll(".profile-tab");
  const panels = {
    overview: document.getElementById("panel-overview"),
    misc: document.getElementById("panel-misc"),
    academic: document.getElementById("panel-academic"),
  };
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const name = tab.getAttribute("data-tab");
      tabs.forEach((t) => {
        t.classList.toggle("active", t === tab);
        t.setAttribute("aria-selected", t === tab ? "true" : "false");
      });
      Object.entries(panels).forEach(([k, el]) => {
        if (!el) return;
        el.classList.toggle("hidden", k !== name);
      });
    });
  });
}

async function main() {
  const role = getRole();
  if (role === "teacher") {
    window.location.href = "/teacher/dashboard/";
    return;
  }
  if (role === "admin") {
    window.location.href = "/admin-panel/dashboard/";
    return;
  }
  if (role !== "student") {
    window.location.href = "/login/";
    return;
  }
  await ensureMeLoaded();
  state.me = getUser();

  try {
    await reload();
  } catch (e) {
    toast.error("Could not load profile", e.message || "Try logging in again.");
    return;
  }

  initTabs();
  document.getElementById("btn-update-email")?.addEventListener("click", openEmailModal);
  document.getElementById("btn-edit-overview")?.addEventListener("click", openEditModal);
  document.getElementById("btn-edit-misc")?.addEventListener("click", openEditModal);
  document.getElementById("btn-edit-academic")?.addEventListener("click", openEditModal);

  document.getElementById("topbar-expand-btn")?.addEventListener("click", () => {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen?.();
    else document.exitFullscreen?.();
  });

  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      document.getElementById("profile-topbar-search-input")?.focus();
    }
  });
}

main();
