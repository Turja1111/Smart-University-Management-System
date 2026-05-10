const containerId = "toast-container";

function container() {
  return document.getElementById(containerId);
}

function icon(type) {
  return { success: "✅", error: "❌", warning: "⚠️", info: "ℹ️" }[type] || "ℹ️";
}

function show(type, title, msg, duration = 4000) {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.innerHTML = `
    <span class="toast-icon">${icon(type)}</span>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      ${msg ? `<div class="toast-msg">${msg}</div>` : ""}
    </div>
    <button class="toast-close" type="button" aria-label="Close">✕</button>
  `;

  const host = container();
  if (!host) return;
  host.appendChild(el);

  el.querySelector(".toast-close")?.addEventListener("click", () => el.remove());

  setTimeout(() => {
    el.classList.add("removing");
    setTimeout(() => el.remove(), 320);
  }, duration);
}

export const toast = {
  show,
  success: (t, m) => show("success", t, m),
  error: (t, m) => show("error", t, m),
  warning: (t, m) => show("warning", t, m),
  info: (t, m) => show("info", t, m),
};

