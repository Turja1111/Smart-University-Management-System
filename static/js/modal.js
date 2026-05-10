function container() {
  return document.getElementById("modal-container");
}

function escHandler(e) {
  if (e.key === "Escape") hide();
}

export function show({ title, body, footer = "" }) {
  const host = container();
  if (!host) return;
  host.innerHTML = `
    <div class="modal-overlay" id="modal-overlay">
      <div class="modal" role="dialog" aria-modal="true">
        <div class="modal-header">
          <h3>${title || ""}</h3>
          <button class="modal-close" id="modal-close-btn" type="button" aria-label="Close">✕</button>
        </div>
        <div class="modal-body">${body || ""}</div>
        ${footer ? `<div class="modal-footer">${footer}</div>` : ""}
      </div>
    </div>
  `;

  document.getElementById("modal-close-btn")?.addEventListener("click", hide);
  document.getElementById("modal-overlay")?.addEventListener("click", (e) => {
    if (e.target?.id === "modal-overlay") hide();
  });
  document.addEventListener("keydown", escHandler);
}

export function hide() {
  const host = container();
  if (host) host.innerHTML = "";
  document.removeEventListener("keydown", escHandler);
}

export function confirm(title, message, onConfirm) {
  show({
    title,
    body: `<p>${message}</p>`,
    footer: `
      <button class="btn btn-secondary" id="modal-cancel-btn" type="button">Cancel</button>
      <button class="btn btn-danger" id="modal-confirm-btn" type="button">Confirm</button>
    `,
  });

  document.getElementById("modal-cancel-btn")?.addEventListener("click", hide);
  document.getElementById("modal-confirm-btn")?.addEventListener("click", () => {
    hide();
    onConfirm?.();
  });
}

