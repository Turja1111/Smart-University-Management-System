import { api, ensureMeLoaded } from "../api.js";
import { setTokens, setUser } from "../auth.js";
import { toast } from "../toast.js";

let selectedRole = "student";

function setRole(role) {
  selectedRole = role;
  document.querySelectorAll("#role-pills .role-pill").forEach((b) => b.classList.toggle("selected", b.dataset.role === role));
}

function setup() {
  document.querySelectorAll("#role-pills .role-pill").forEach((b) => b.addEventListener("click", () => setRole(b.dataset.role)));

  document.getElementById("register-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("reg-submit-btn");
    const first_name = document.getElementById("reg-first").value.trim();
    const last_name = document.getElementById("reg-last").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const username = `${first_name}.${last_name}`
      .toLowerCase()
      .replace(/[^a-z0-9.]/g, "")
      .replace(/\.+/g, ".")
      .replace(/^\./, "")
      .replace(/\.$/, "") || email.split("@")[0];
    const password = document.getElementById("reg-pass").value;
    const password_confirm = document.getElementById("reg-pass2").value;

    if (password !== password_confirm) {
      toast.error("Passwords do not match", "");
      return;
    }

    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Creating account…`;
    try {
      const data = await api.auth.register({ first_name, last_name, email, username, password, password_confirm, role: selectedRole });
      const tokens = data.tokens || {};
      setTokens({ access: tokens.access, refresh: tokens.refresh });
      if (data.user) setUser(data.user);
      await ensureMeLoaded();
      toast.success("Account created!", "");
      window.location.href = selectedRole === "teacher" ? "/teacher/dashboard/" : "/student/dashboard/";
    } catch (err) {
      const msgs = err?.data;
      const msg =
        msgs && typeof msgs === "object"
          ? Object.entries(msgs)
              .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(" ") : String(v)}`)
              .join("  ")
          : "Registration failed.";
      // Prefer specific validation feedback over a generic title.
      toast.error(msg, "");
      btn.disabled = false;
      btn.textContent = "Create Account";
    }
  });
}

setup();

