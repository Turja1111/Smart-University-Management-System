import { api, ensureMeLoaded } from "../api.js";
import { setTokens, setUser } from "../auth.js";
import { toast } from "../toast.js";

let selectedRole = "student";

function rolePills() {
  return document.querySelectorAll("#role-pills .role-pill");
}

function setRole(role) {
  selectedRole = role;
  rolePills().forEach((b) => b.classList.toggle("selected", b.dataset.role === role));
}

function dashboardFor(role) {
  if (role === "admin") return "/admin-panel/dashboard/";
  if (role === "teacher") return "/teacher/dashboard/";
  return "/student/dashboard/";
}

function setup() {
  rolePills().forEach((b) => b.addEventListener("click", () => setRole(b.dataset.role)));

  document.getElementById("login-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("login-submit-btn");
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Signing in…`;

    try {
      const data = await api.auth.login({ email, password });
      setTokens({ access: data.access, refresh: data.refresh });
      if (data.user) setUser(data.user);
      await ensureMeLoaded();
      toast.success("Welcome back!", "");
      window.location.href = dashboardFor(selectedRole);
    } catch (err) {
      const msg = err?.data?.detail || err?.data?.non_field_errors?.[0] || "Invalid credentials.";
      // Show the most specific message as the primary text (not a generic "Login failed").
      toast.error(msg, "");
      btn.disabled = false;
      btn.textContent = "Sign In";
    }
  });
}

setup();

